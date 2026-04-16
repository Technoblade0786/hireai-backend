from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import JobSeekerProfile, EmployerProfile, Job, Application
from .serializers import (RegisterSerializer, UserSerializer, JobSeekerProfileSerializer,
                           EmployerProfileSerializer, JobSerializer, JobListSerializer,
                           ApplicationSerializer)
from .ai_matching import get_recommended_jobs, calculate_match_score

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


# --- Seeker Profile ---
class SeekerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer

    def get_object(self):
        profile, _ = JobSeekerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# --- Employer Profile ---
class EmployerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployerProfileSerializer

    def get_object(self):
        profile, _ = EmployerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


# --- Jobs ---
class JobListView(generics.ListAPIView):
    serializer_class = JobListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Job.objects.filter(is_active=True).select_related('employer')
        search = self.request.query_params.get('search', '')
        job_type = self.request.query_params.get('type', '')
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(required_skills__icontains=search)
        if job_type:
            qs = qs.filter(job_type=job_type)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # AI recommendations if logged in as seeker
        match_scores = {}
        if request.user.is_authenticated and request.user.role == 'seeker':
            try:
                seeker = request.user.seeker_profile
                scored = get_recommended_jobs(seeker, queryset, top_n=100)
                # Sort by score
                queryset = [job for job, score in scored]
                match_scores = {job.id: score for job, score in scored}
            except JobSeekerProfile.DoesNotExist:
                pass

        request.match_scores = match_scores
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobCreateView(generics.CreateAPIView):
    serializer_class = JobSerializer

    def perform_create(self, serializer):
        employer = self.request.user.employer_profile
        serializer.save(employer=employer)


class JobUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user.employer_profile)


# --- Applications ---
class ApplyView(APIView):
    def post(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id, is_active=True)
            seeker = request.user.seeker_profile
        except (Job.DoesNotExist, JobSeekerProfile.DoesNotExist):
            return Response({'error': 'Job not found or profile incomplete'}, status=404)

        if Application.objects.filter(job=job, applicant=seeker).exists():
            return Response({'error': 'Already applied'}, status=400)

        score = calculate_match_score(
            seeker.skills_list(), job.required_skills_list(),
            seeker.experience_years, job.experience_required
        )

        app = Application.objects.create(
            job=job,
            applicant=seeker,
            cover_letter=request.data.get('cover_letter', ''),
            match_score=score
        )
        return Response(ApplicationSerializer(app).data, status=201)


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(
            applicant=self.request.user.seeker_profile
        ).select_related('job', 'job__employer')


class JobApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        job_id = self.kwargs['job_id']
        return Application.objects.filter(
            job_id=job_id,
            job__employer=self.request.user.employer_profile
        ).select_related('applicant').order_by('-match_score')


class UpdateApplicationStatusView(APIView):
    def patch(self, request, app_id):
        try:
            app = Application.objects.get(
                id=app_id,
                job__employer=request.user.employer_profile
            )
        except Application.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        new_status = request.data.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            app.status = new_status
            app.save()
            return Response(ApplicationSerializer(app).data)
        return Response({'error': 'Invalid status'}, status=400)


# --- Dashboard Stats ---
class DashboardView(APIView):
    def get(self, request):
        user = request.user
        if user.role == 'seeker':
            try:
                seeker = user.seeker_profile
                apps = Application.objects.filter(applicant=seeker)
                return Response({
                    'total_applications': apps.count(),
                    'shortlisted': apps.filter(status='shortlisted').count(),
                    'hired': apps.filter(status='hired').count(),
                    'pending': apps.filter(status='applied').count(),
                })
            except:
                return Response({'total_applications': 0, 'shortlisted': 0, 'hired': 0, 'pending': 0})
        else:
            try:
                employer = user.employer_profile
                jobs = Job.objects.filter(employer=employer)
                total_apps = Application.objects.filter(job__in=jobs).count()
                return Response({
                    'total_jobs': jobs.count(),
                    'active_jobs': jobs.filter(is_active=True).count(),
                    'total_applications': total_apps,
                })
            except:
                return Response({'total_jobs': 0, 'active_jobs': 0, 'total_applications': 0})

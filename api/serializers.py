from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, EmployerProfile, Job, Application

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['seeker', 'employer'])

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role']


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'
        read_only_fields = ['user']


class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = '__all__'
        read_only_fields = ['user']


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='employer.company_name', read_only=True)
    company_location = serializers.CharField(source='employer.location', read_only=True)

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['employer']


class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='employer.company_name', read_only=True)
    match_score = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'company_name', 'location', 'job_type',
                  'salary_min', 'salary_max', 'required_skills', 'experience_required',
                  'created_at', 'match_score']

    def get_match_score(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'match_scores'):
            return request.match_scores.get(obj.id, None)
        return None


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.employer.company_name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    applicant_skills = serializers.CharField(source='applicant.skills', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['applicant', 'match_score', 'status']

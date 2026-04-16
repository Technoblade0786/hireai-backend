from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [('seeker', 'Job Seeker'), ('employer', 'Employer')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='seeker')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seeker_profile')
    full_name = models.CharField(max_length=100)
    skills = models.TextField(help_text="Comma separated skills e.g. Python, Django, SQL")
    experience_years = models.IntegerField(default=0)
    education = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    resume_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def skills_list(self):
        return [s.strip().lower() for s in self.skills.split(',') if s.strip()]

    def __str__(self):
        return self.full_name


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    company_size = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
    ]
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma separated required skills")
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    experience_required = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def required_skills_list(self):
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]

    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    match_score = models.FloatField(default=0.0)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.full_name} -> {self.job.title}"

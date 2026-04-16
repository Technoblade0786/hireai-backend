from django.contrib import admin
from .models import User, JobSeekerProfile, EmployerProfile, Job, Application

admin.site.register(User)
admin.site.register(JobSeekerProfile)
admin.site.register(EmployerProfile)
admin.site.register(Job)
admin.site.register(Application)
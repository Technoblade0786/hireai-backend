from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('auth/me/', views.MeView.as_view()),

    # Profiles
    path('profile/seeker/', views.SeekerProfileView.as_view()),
    path('profile/employer/', views.EmployerProfileView.as_view()),

    # Jobs
    path('jobs/', views.JobListView.as_view()),
    path('jobs/<int:pk>/', views.JobDetailView.as_view()),
    path('jobs/create/', views.JobCreateView.as_view()),
    path('jobs/<int:pk>/manage/', views.JobUpdateDeleteView.as_view()),
    path('jobs/<int:job_id>/apply/', views.ApplyView.as_view()),
    path('jobs/<int:job_id>/applications/', views.JobApplicationsView.as_view()),

    # Applications
    path('applications/mine/', views.MyApplicationsView.as_view()),
    path('applications/<int:app_id>/status/', views.UpdateApplicationStatusView.as_view()),

    # Dashboard
    path('dashboard/', views.DashboardView.as_view()),
]

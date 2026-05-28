from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import TemplateView

def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "Backend is running"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check),
]

from django.urls import path
from . import views

urlpatterns = [
    # 1. Landing & Selection
    path('', views.index, name='index'),
    path('selection/', views.selection, name='selection'),

    # 2. Admin Side
    path('admin-signup/', views.admin_signup, name='admin_signup'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-job/<str:job_id>/', views.delete_job, name='delete_job'),
    path('generate-admin-token/', views.generate_admin_token, name='generate_admin_token'),
    path('registration-success/', views.registration_success, name='registration_success'),

    # 3. Graduate Side
    path('grad-signup/', views.grad_signup, name='grad_signup'),
    path('grad-login/', views.grad_login, name='grad_login'),
    path('grad-dashboard/', views.grad_dashboard, name='grad_dashboard'),
    
    # 4. Shared Actions
    # This MUST match the function name 'handle_logout' in your views.py
    path('logout/', views.handle_logout, name='logout'),
]

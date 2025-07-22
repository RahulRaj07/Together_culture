from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('login/', views.login_user, name='login'),
    path('apply/', views.apply_for_membership, name='apply'),
    path('application-success/', views.application_success, name='application_success'),
    path('admin-dashboard/', views.admin_home, name='admin_home'),
    path('approve/<int:member_id>/', views.approve_member, name='approve_member'),
    path('member-details/<int:member_id>/', views.member_details, name='member_details'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]

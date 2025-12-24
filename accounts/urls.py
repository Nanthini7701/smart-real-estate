from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login/owner/', views.login_owner, name='login_owner'),
    path('login/tenant/', views.login_tenant, name='login_tenant'),
    path('logout/', views.logout_view, name='logout'),

    path('signup/owner/', views.signup_owner, name='signup_owner'),
    path('signup/tenant/', views.signup_tenant, name='signup_tenant'),
]
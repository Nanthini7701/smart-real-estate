from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from .forms import OwnerSignupForm, TenantSignupForm

def home(request):
    if request.user.is_authenticated:
        if request.user.is_owner:
            return redirect('owner_dashboard')
        elif request.user.is_tenant:
            return redirect('tenant_dashboard')
    return redirect('login')
def signup_owner(request):
    form = OwnerSignupForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_owner = True
        user.save()
        login(request, user)
        return redirect('owner_dashboard')
    return render(request, 'signup_owner.html', {'form': form})

def signup_tenant(request):
    form = TenantSignupForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_tenant = True
        user.save()
        login(request, user)
        return redirect('tenant_dashboard')
    return render(request, 'signup_tenant.html', {'form': form})

def login_view(request):
    # Generic login — will redirect based on role
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)

        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return redirect(next_url)

        if user.is_owner:
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('owner_dashboard')
        if user.is_tenant:
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('tenant_dashboard')

        messages.info(request, 'Logged in successfully.')
        return redirect('tenant_dashboard')

    return render(request, 'login.html', {'form': form})


def login_owner(request):
    # Login page specifically for owners
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        if not user.is_owner:
            messages.error(request, 'This account is not registered as an owner. Use tenant login or sign up as owner.')
            return render(request, 'login.html', {'form': form, 'role': 'owner'})
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('owner_dashboard')
    return render(request, 'login.html', {'form': form, 'role': 'owner'})


def login_tenant(request):
    # Login page specifically for tenants
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        if not user.is_tenant:
            messages.error(request, 'This account is not registered as a tenant. Use owner login or sign up as tenant.')
            return render(request, 'login.html', {'form': form, 'role': 'tenant'})
        login(request, user)
        messages.success(request, f'Welcome back, {user.username}!')
        return redirect('tenant_dashboard')
    return render(request, 'login.html', {'form': form, 'role': 'tenant'})

def logout_view(request):
    logout(request)
    return redirect('login')

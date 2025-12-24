from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class OwnerSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

class TenantSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

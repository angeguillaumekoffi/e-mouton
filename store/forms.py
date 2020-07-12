from django import forms
from django.contrib.auth.models import User
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password= forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)
    remember_me = forms.BooleanField(label="Mémoriser ma session", required=False, initial=False)
    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']

class InscrireForm(forms.Form):
    password1 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput)
    username = forms.CharField(max_length=100, required=True)
    email= forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
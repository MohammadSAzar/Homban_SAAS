from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from . import models


class AdminCustomUserCreationForm(UserCreationForm):
    class Meta:
        model = models.CustomUserModel
        fields = ('username',)


class AdminCustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.CustomUserModel
        fields = UserChangeForm.Meta.fields


class LoginForm(forms.ModelForm):
    class Meta:
        model = models.CustomUserModel
        fields = ['username', 'password']


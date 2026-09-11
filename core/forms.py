from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Team, Project


class RegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ["name", "description"]


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "description"]
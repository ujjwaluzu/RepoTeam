from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Team, Project, Issue


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


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
        ]

    def __init__(self, *args, assigned_users=None, **kwargs):
        super().__init__(*args, **kwargs)

        if assigned_users is not None:
            self.fields["assigned_to"].queryset = assigned_users
        
class InviteMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter a username",
            }
        ),
    )
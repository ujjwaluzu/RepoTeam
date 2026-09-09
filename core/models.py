from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = 'O', 'Owner'
        ADMIN = 'A', 'Admin'
        MEMBER = 'M','Member'


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=1,
        choices=Role.choices,
    )
    joined_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'team'],
                name='unique_team_membership'
            )
        ]

class Project(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=500)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Issue(models.Model):
    class Status(models.TextChoices):
        TODO = 'T', 'Todo'
        IN_PROGRESS = 'IP', 'In Progress'
        IN_REVIEW = 'IR','In Review'
        DONE = 'D', 'Done'
    class Priority(models.TextChoices):
        LOW = 'L', 'Low'
        MEDIUM = 'M', 'Medium'
        HIGH = 'H', 'High'

    title = models.CharField(max_length=50)
    description = models.TextField(max_length=500)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_issues')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.TODO
    )
    priority = models.CharField(
        max_length=1,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
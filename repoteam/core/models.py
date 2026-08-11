from django.db import models


class Profile(models.Model):
    """Public collaboration profile attached to a Django user."""

    class Experience(models.TextChoices):
        JUNIOR = "Junior", "Junior"
        MID_LEVEL = "Mid-level", "Mid-level"
        SENIOR = "Senior", "Senior"

    class Availability(models.TextChoices):
        OPEN = "Open to collaborate", "Open to collaborate"
        LOOKING = "Looking for teammates", "Looking for teammates"
        PART_TIME = "Available part-time", "Available part-time"
        UNAVAILABLE = "Not currently available", "Not currently available"

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience = models.CharField(max_length=20, choices=Experience.choices, blank=True)
    availability = models.CharField(max_length=40, choices=Availability.choices, default=Availability.OPEN)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username

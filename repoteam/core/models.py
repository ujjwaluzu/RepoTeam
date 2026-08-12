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


class Project(models.Model):
    """A collaborative project owned by a single RepoTeam user."""

    class ProjectType(models.TextChoices):
        OPEN_SOURCE = "Open source", "Open source"
        COMMUNITY = "Community", "Community"
        SIDE_PROJECT = "Side project", "Side project"
        LEARNING = "Learning", "Learning"

    class Difficulty(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"

    class Status(models.TextChoices):
        RECRUITING = "Recruiting", "Recruiting"
        PLANNING = "Planning", "Planning"
        IN_PROGRESS = "In progress", "In progress"
        PAUSED = "Paused", "Paused"
        COMPLETED = "Completed", "Completed"

    class WorkflowStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="owned_projects")
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=190, unique=True)
    short_description = models.TextField(max_length=500)
    description = models.TextField(blank=True)
    repository_url = models.URLField(blank=True)
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    team_capacity = models.PositiveSmallIntegerField(default=5)
    technologies = models.JSONField(default=list, blank=True)
    workflow_status = models.CharField(max_length=12, choices=WorkflowStatus.choices, default=WorkflowStatus.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "title"]

    def __str__(self):
        return self.title


class ProjectRole(models.Model):
    """An open contributor role belonging to a project."""

    class Experience(models.TextChoices):
        ANY = "Any experience", "Any experience"
        JUNIOR = "Junior", "Junior"
        MID_LEVEL = "Mid-level", "Mid-level"
        SENIOR = "Senior", "Senior"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="roles")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    required_skills = models.JSONField(default=list, blank=True)
    experience = models.CharField(max_length=20, choices=Experience.choices, default=Experience.ANY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.project.title}: {self.title}"

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


class ProjectMembership(models.Model):
    """An active user membership in a project."""

    class MemberRole(models.TextChoices):
        OWNER = "owner", "Owner"
        CONTRIBUTOR = "contributor", "Contributor"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="project_memberships")
    role = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True, blank=True, related_name="memberships")
    member_role = models.CharField(max_length=20, choices=MemberRole.choices, default=MemberRole.CONTRIBUTOR)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["joined_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["project", "user"], name="unique_project_membership"),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.project.title}"


class ProjectApplication(models.Model):
    """A user's request to join a project role."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        WITHDRAWN = "withdrawn", "Withdrawn"
        REJECTED = "rejected", "Rejected"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="project_applications")
    role = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_project_applications")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["applicant", "status"]),
        ]

    def __str__(self):
        return f"{self.applicant.username} application for {self.project.title}"


class ActivityEvent(models.Model):
    """A durable event used to build personalised workspace activity feeds."""

    class EventType(models.TextChoices):
        PROJECT_CREATED = "project_created", "Project created"
        PROJECT_PUBLISHED = "project_published", "Project published"
        MEMBER_JOINED = "member_joined", "Member joined"
        APPLICATION_SUBMITTED = "application_submitted", "Application submitted"
        APPLICATION_ACCEPTED = "application_accepted", "Application accepted"
        APPLICATION_REJECTED = "application_rejected", "Application rejected"
        APPLICATION_WITHDRAWN = "application_withdrawn", "Application withdrawn"

    event_type = models.CharField(max_length=40, choices=EventType.choices)
    actor = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="activity_events")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="activity_events")
    application = models.ForeignKey(ProjectApplication, on_delete=models.CASCADE, null=True, blank=True, related_name="activity_events")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["project", "created_at"]),
            models.Index(fields=["actor", "created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.project or 'workspace'})"


class Notification(models.Model):
    """A private, durable in-app notification for a user."""

    class NotificationType(models.TextChoices):
        APPLICATION = "application", "Application"
        DECISION = "decision", "Decision"
        INVITATION = "invitation", "Invitation"
        PROJECT_UPDATE = "project_update", "Project update"

    recipient = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=160)
    body = models.TextField()
    actor = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_notifications")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    application = models.ForeignKey(ProjectApplication, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "created_at"], name="core_notif_rec_read_5ab6bf_idx"),
            models.Index(fields=["recipient", "created_at"], name="core_notif_rec_time_e1b8f0_idx"),
        ]

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"


class UserPreference(models.Model):
    """Cross-device notification, privacy, and appearance preferences."""

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="preferences")
    email_applications = models.BooleanField(default=True)
    email_decisions = models.BooleanField(default=True)
    email_invitations = models.BooleanField(default=True)
    email_project_updates = models.BooleanField(default=True)
    show_availability = models.BooleanField(default=True)
    show_activity = models.BooleanField(default=True)
    compact_project_cards = models.BooleanField(default=False)
    reduce_motion = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"

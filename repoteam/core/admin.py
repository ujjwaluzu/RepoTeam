from django.contrib import admin
from .models import Notification, Profile, Project, ProjectApplication, ProjectMembership, ProjectRole, UserPreference


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "experience", "availability", "is_public")
    list_filter = ("experience", "availability", "is_public")
    search_fields = ("user__username", "display_name", "location")


class ProjectRoleInline(admin.TabularInline):
    model = ProjectRole
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "project_type", "difficulty", "status", "workflow_status", "updated_at")
    list_filter = ("project_type", "difficulty", "status", "workflow_status")
    search_fields = ("title", "short_description", "owner__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ProjectRoleInline,)


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "member_role", "role", "joined_at")
    list_filter = ("member_role",)
    search_fields = ("project__title", "user__username", "role__title")


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    list_display = ("project", "applicant", "role", "status", "created_at", "reviewed_at")
    list_filter = ("status",)
    search_fields = ("project__title", "applicant__username", "role__title")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "title", "project", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("recipient__username", "title", "body", "project__title")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "email_applications", "email_decisions", "show_availability", "show_activity", "updated_at")
    list_filter = ("email_applications", "email_decisions", "show_availability", "show_activity", "reduce_motion")
    search_fields = ("user__username", "user__email")

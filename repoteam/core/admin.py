from django.contrib import admin
from .models import Profile, Project, ProjectRole


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

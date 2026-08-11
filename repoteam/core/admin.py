from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "experience", "availability", "is_public")
    list_filter = ("experience", "availability", "is_public")
    search_fields = ("user__username", "display_name", "location")

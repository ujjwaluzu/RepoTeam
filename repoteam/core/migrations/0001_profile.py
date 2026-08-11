from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Profile", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("display_name", models.CharField(blank=True, max_length=120)), ("title", models.CharField(blank=True, max_length=160)),
        ("bio", models.TextField(blank=True)), ("location", models.CharField(blank=True, max_length=120)),
        ("skills", models.JSONField(blank=True, default=list)),
        ("experience", models.CharField(blank=True, choices=[("Junior", "Junior"), ("Mid-level", "Mid-level"), ("Senior", "Senior")], max_length=20)),
        ("availability", models.CharField(choices=[("Open to collaborate", "Open to collaborate"), ("Looking for teammates", "Looking for teammates"), ("Available part-time", "Available part-time"), ("Not currently available", "Not currently available")], default="Open to collaborate", max_length=40)),
        ("github_url", models.URLField(blank=True)), ("linkedin_url", models.URLField(blank=True)), ("is_public", models.BooleanField(default=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ("user", models.OneToOneField(on_delete=models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
    ])]

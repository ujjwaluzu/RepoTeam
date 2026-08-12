from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_profile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("slug", models.SlugField(max_length=190, unique=True)),
                ("short_description", models.TextField(max_length=500)),
                ("description", models.TextField(blank=True)),
                ("repository_url", models.URLField(blank=True)),
                ("project_type", models.CharField(choices=[("Open source", "Open source"), ("Community", "Community"), ("Side project", "Side project"), ("Learning", "Learning")], max_length=30)),
                ("difficulty", models.CharField(choices=[("Beginner", "Beginner"), ("Intermediate", "Intermediate"), ("Advanced", "Advanced")], max_length=20)),
                ("status", models.CharField(choices=[("Recruiting", "Recruiting"), ("Planning", "Planning"), ("In progress", "In progress"), ("Paused", "Paused"), ("Completed", "Completed")], default="Planning", max_length=20)),
                ("team_capacity", models.PositiveSmallIntegerField(default=5)),
                ("technologies", models.JSONField(blank=True, default=list)),
                ("workflow_status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft", max_length=12)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="owned_projects", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at", "title"]},
        ),
        migrations.CreateModel(
            name="ProjectRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("required_skills", models.JSONField(blank=True, default=list)),
                ("experience", models.CharField(choices=[("Any experience", "Any experience"), ("Junior", "Junior"), ("Mid-level", "Mid-level"), ("Senior", "Senior")], default="Any experience", max_length=20)),
                ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed")], default="open", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="core.project")),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]

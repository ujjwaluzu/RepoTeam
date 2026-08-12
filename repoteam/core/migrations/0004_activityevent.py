from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_projectmembership_projectapplication"),
    ]

    operations = [
        migrations.CreateModel(
            name="ActivityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[
                    ("project_created", "Project created"),
                    ("project_published", "Project published"),
                    ("member_joined", "Member joined"),
                    ("application_submitted", "Application submitted"),
                    ("application_accepted", "Application accepted"),
                    ("application_rejected", "Application rejected"),
                    ("application_withdrawn", "Application withdrawn"),
                ], max_length=40)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activity_events", to=settings.AUTH_USER_MODEL)),
                ("application", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activity_events", to="core.projectapplication")),
                ("project", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="activity_events", to="core.project")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(
            model_name="activityevent",
            index=models.Index(fields=["project", "created_at"], name="core_activit_project_6e75f9_idx"),
        ),
        migrations.AddIndex(
            model_name="activityevent",
            index=models.Index(fields=["actor", "created_at"], name="core_activit_actor_i_8c8151_idx"),
        ),
    ]

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Profile, Project, ProjectRole


class ProfileApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "safe-password-123")
        self.profile = Profile.objects.create(user=self.user, display_name="Alex Rivera", title="Frontend engineer", skills=["React", "TypeScript"], experience="Senior")

    def test_public_developer_list_can_filter_by_skill(self):
        response = self.client.get("/api/developers/?skill=React")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["username"], "alex")
        self.assertEqual(response.json()["page"], 1)
        self.assertFalse(response.json()["has_next"])

    def test_private_profiles_are_not_publicly_visible(self):
        self.profile.is_public = False
        self.profile.save()
        response = self.client.get("/api/developers/alex/")
        self.assertEqual(response.status_code, 404)

    def test_authenticated_user_can_update_own_profile(self):
        self.client.force_login(self.user)
        response = self.client.patch("/api/profile/me/", data={"bio": "I build useful interfaces.", "skills": ["React", "Accessibility"]}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "I build useful interfaces.")
        self.assertEqual(self.profile.skills, ["React", "Accessibility"])

    def test_profile_update_requires_login(self):
        response = self.client.patch("/api/profile/me/", data="{}", content_type="application/json")
        self.assertEqual(response.status_code, 401)


class ProjectApiTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="safe-password-123")
        Profile.objects.create(user=self.owner, display_name="Project Owner")
        self.other = User.objects.create_user("other", password="safe-password-123")

    def payload(self, **overrides):
        payload = {
            "title": "Open Study",
            "short_description": "A peer-powered study space.",
            "description": "A longer project story.",
            "repository_url": "https://github.com/example/open-study",
            "project_type": "Community",
            "difficulty": "Beginner",
            "status": "Recruiting",
            "team_capacity": 6,
            "technologies": ["React", "Django"],
            "roles": [{"title": "Frontend Developer", "description": "Build the UI.", "required_skills": ["React"], "experience": "Mid-level"}],
            "workflow_status": "published",
        }
        payload.update(overrides)
        return payload

    def test_create_project_requires_authentication(self):
        response = self.client.post("/api/projects/", data=self.payload(), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_owner_can_create_publish_and_list_project_with_roles(self):
        self.client.force_login(self.owner)
        response = self.client.post("/api/projects/", data=self.payload(), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.assertEqual(project.owner, self.owner)
        self.assertEqual(project.workflow_status, "published")
        self.assertEqual(project.roles.count(), 1)
        listing = self.client.get("/api/projects/?q=study&technology=React&page_size=1")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["count"], 1)
        self.assertEqual(listing.json()["results"][0]["roles"][0]["title"], "Frontend Developer")
        detail = self.client.get(f"/api/projects/{project.slug}/")
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(detail.json()["project"]["is_owner"])

    def test_drafts_are_private_and_owner_can_publish(self):
        self.client.force_login(self.owner)
        response = self.client.post("/api/projects/", data=self.payload(workflow_status="draft"), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.client.logout()
        self.assertEqual(self.client.get("/api/projects/").json()["count"], 0)
        self.assertEqual(self.client.get(f"/api/projects/{project.slug}/").status_code, 404)
        self.client.force_login(self.owner)
        response = self.client.post(f"/api/projects/{project.slug}/publish/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project"]["workflow_status"], "published")

    def test_only_owner_can_update_or_archive(self):
        self.client.force_login(self.owner)
        self.client.post("/api/projects/", data=self.payload(), content_type="application/json")
        project = Project.objects.get()
        self.client.force_login(self.other)
        self.assertEqual(self.client.patch(f"/api/projects/{project.slug}/", data={"title": "Nope"}, content_type="application/json").status_code, 403)
        self.assertEqual(self.client.post(f"/api/projects/{project.slug}/archive/").status_code, 403)
        self.client.force_login(self.owner)
        response = self.client.patch(f"/api/projects/{project.slug}/", data={"title": "Open Study Updated", "roles": []}, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        project.refresh_from_db()
        self.assertEqual(project.title, "Open Study Updated")
        self.assertEqual(project.roles.count(), 0)

    def test_project_validation_returns_consistent_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post("/api/projects/", data={"title": ""}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

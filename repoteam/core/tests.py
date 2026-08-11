from django.test import TestCase
from django.contrib.auth.models import User

from .models import Profile


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

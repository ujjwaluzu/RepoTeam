from django.test import TestCase
from django.contrib.auth.models import User

from .models import ActivityEvent, Profile, Project, ProjectApplication, ProjectMembership, ProjectRole


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


class MembershipAndApplicationApiTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="safe-password-123")
        Profile.objects.create(user=self.owner, display_name="Owner")
        self.applicant = User.objects.create_user("applicant", password="safe-password-123")
        Profile.objects.create(user=self.applicant, display_name="Applicant")
        self.other = User.objects.create_user("other", password="safe-password-123")
        self.project = Project.objects.create(
            owner=self.owner,
            title="Community Garden",
            slug="community-garden",
            short_description="A shared project.",
            project_type=Project.ProjectType.COMMUNITY,
            difficulty=Project.Difficulty.BEGINNER,
            status=Project.Status.RECRUITING,
            team_capacity=3,
            workflow_status=Project.WorkflowStatus.PUBLISHED,
        )
        self.role = ProjectRole.objects.create(project=self.project, title="Frontend Developer", required_skills=["React"])
        ProjectMembership.objects.create(project=self.project, user=self.owner, member_role=ProjectMembership.MemberRole.OWNER)

    def test_join_project_creates_membership_and_duplicate_is_rejected(self):
        self.client.force_login(self.applicant)
        self.project.team_capacity = 1
        self.project.save(update_fields=["team_capacity"])
        full = self.client.post(f"/api/projects/{self.project.slug}/join/")
        self.assertEqual(full.status_code, 400)
        self.project.team_capacity = 3
        self.project.save(update_fields=["team_capacity"])
        response = self.client.post(f"/api/projects/{self.project.slug}/join/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ProjectMembership.objects.filter(project=self.project).count(), 2)
        duplicate = self.client.post(f"/api/projects/{self.project.slug}/join/")
        self.assertEqual(duplicate.status_code, 400)

    def test_apply_review_and_dashboard_boxes(self):
        self.client.force_login(self.applicant)
        response = self.client.post(
            f"/api/projects/{self.project.slug}/roles/{self.role.id}/apply/",
            data={"message": "I would love to help."},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        application = ProjectApplication.objects.get()
        self.assertEqual(application.status, ProjectApplication.Status.PENDING)
        self.assertEqual(self.client.get("/api/applications/?kind=sent").json()["count"], 1)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/api/applications/?kind=received").json()["count"], 1)
        accepted = self.client.post(f"/api/applications/{application.id}/accept/")
        self.assertEqual(accepted.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, ProjectApplication.Status.ACCEPTED)
        self.assertTrue(ProjectMembership.objects.filter(project=self.project, user=self.applicant, role=self.role).exists())

    def test_duplicate_pending_application_capacity_and_withdrawal(self):
        self.client.force_login(self.applicant)
        payload = {"role_id": self.role.id, "message": "Please consider me."}
        self.assertEqual(self.client.post(f"/api/projects/{self.project.slug}/apply/", data=payload, content_type="application/json").status_code, 201)
        duplicate = self.client.post(f"/api/projects/{self.project.slug}/apply/", data=payload, content_type="application/json")
        self.assertEqual(duplicate.status_code, 400)
        application = ProjectApplication.objects.get()
        self.assertEqual(self.client.post(f"/api/applications/{application.id}/withdraw/").status_code, 200)
        self.assertEqual(self.client.post(f"/api/projects/{self.project.slug}/apply/", data=payload, content_type="application/json").status_code, 201)

    def test_only_owner_can_review_and_project_members_are_visible(self):
        self.client.force_login(self.applicant)
        self.client.post(f"/api/projects/{self.project.slug}/apply/", data={"role_id": self.role.id}, content_type="application/json")
        application = ProjectApplication.objects.get()
        self.assertEqual(self.client.post(f"/api/applications/{application.id}/reject/").status_code, 403)
        self.client.force_login(self.owner)
        members = self.client.get(f"/api/projects/{self.project.slug}/members/")
        self.assertEqual(members.status_code, 200)
        self.assertEqual(members.json()["count"], 1)

    def test_dashboard_returns_real_counts_activity_and_recommendations(self):
        Profile.objects.get(user=self.applicant).skills = ["React"]
        Profile.objects.get(user=self.applicant).availability = Profile.Availability.OPEN
        Profile.objects.get(user=self.applicant).save()
        recommended = Project.objects.create(
            owner=self.owner,
            title="React Community",
            slug="react-community",
            short_description="A React project.",
            project_type=Project.ProjectType.COMMUNITY,
            difficulty=Project.Difficulty.BEGINNER,
            status=Project.Status.RECRUITING,
            workflow_status=Project.WorkflowStatus.PUBLISHED,
            technologies=["React"],
        )
        ProjectRole.objects.create(project=recommended, title="Frontend", required_skills=["React"])
        self.client.force_login(self.applicant)
        self.client.post(f"/api/projects/{self.project.slug}/join/")
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["contributing_projects"], 1)
        self.assertEqual(payload["summary"]["contributions"], 1)
        self.assertTrue(any(item["event_type"] == ActivityEvent.EventType.MEMBER_JOINED for item in payload["activity"]))
        self.assertEqual(payload["recommendations"][0]["slug"], recommended.slug)
        self.assertIn("React", payload["recommendations"][0]["matched_skills"])

    def test_dashboard_requires_authentication(self):
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 401)

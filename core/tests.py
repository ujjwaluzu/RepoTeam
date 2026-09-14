from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Team, Membership, Project, Issue


class PageRenderTests(TestCase):
    """Verify every page renders without template errors."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="alice", password="testpass123", email="alice@example.com"
        )
        self.other_user = User.objects.create_user(
            username="bob", password="testpass123", email="bob@example.com"
        )
        self.team = Team.objects.create(
            name="Test Team", description="A test team", created_by=self.user
        )
        self.membership = Membership.objects.create(
            user=self.user, team=self.team, role=Membership.Role.OWNER
        )
        self.other_membership = Membership.objects.create(
            user=self.other_user, team=self.team, role=Membership.Role.MEMBER
        )
        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            team=self.team,
            created_by=self.user,
        )
        self.issue = Issue.objects.create(
            title="Test Issue",
            description="A test issue",
            project=self.project,
            created_by=self.user,
            assigned_to=self.other_user,
            status=Issue.Status.TODO,
            priority=Issue.Priority.MEDIUM,
        )

    def test_index(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_login(self):
        r = self.client.get("/login/")
        self.assertEqual(r.status_code, 200)

    def test_register(self):
        r = self.client.get("/register/")
        self.assertEqual(r.status_code, 200)

    def test_dashboard_requires_login(self):
        r = self.client.get("/dashboard/")
        self.assertEqual(r.status_code, 302)

    def test_dashboard(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get("/dashboard/")
        self.assertEqual(r.status_code, 200)

    def test_create_team(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get("/teams/create/")
        self.assertEqual(r.status_code, 200)

    def test_team_detail(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/teams/{self.team.id}/")
        self.assertEqual(r.status_code, 200)

    def test_create_project(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/teams/{self.team.id}/projects/create/")
        self.assertEqual(r.status_code, 200)

    def test_project_detail(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/projects/{self.project.id}/")
        self.assertEqual(r.status_code, 200)

    def test_create_issue(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/projects/{self.project.id}/issues/create/")
        self.assertEqual(r.status_code, 200)

    def test_edit_issue(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/issues/{self.issue.id}/edit/")
        self.assertEqual(r.status_code, 200)

    def test_delete_issue(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/issues/{self.issue.id}/delete/")
        self.assertEqual(r.status_code, 200)

    def test_invite_member(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(f"/teams/{self.team.id}/invite/")
        self.assertEqual(r.status_code, 200)

    def test_remove_member(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(
            f"/teams/{self.team.id}/members/{self.other_user.id}/remove/"
        )
        self.assertEqual(r.status_code, 200)

    def test_change_member_role(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.get(
            f"/teams/{self.team.id}/members/{self.other_user.id}/role/"
        )
        self.assertEqual(r.status_code, 200)

    def test_member_cannot_invite(self):
        self.client.login(username="bob", password="testpass123")
        r = self.client.get(f"/teams/{self.team.id}/invite/")
        self.assertEqual(r.status_code, 302)

    def test_member_cannot_remove(self):
        self.client.login(username="bob", password="testpass123")
        r = self.client.get(
            f"/teams/{self.team.id}/members/{self.other_user.id}/remove/"
        )
        self.assertEqual(r.status_code, 302)

    def test_member_cannot_change_role(self):
        self.client.login(username="bob", password="testpass123")
        r = self.client.get(
            f"/teams/{self.team.id}/members/{self.other_user.id}/role/"
        )
        self.assertEqual(r.status_code, 302)

    def test_create_team_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            "/teams/create/", {"name": "New Team", "description": "Desc"}
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Team.objects.filter(name="New Team").exists())

    def test_create_project_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/teams/{self.team.id}/projects/create/",
            {"name": "New Project", "description": "Desc"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Project.objects.filter(name="New Project").exists())

    def test_create_issue_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/projects/{self.project.id}/issues/create/",
            {
                "title": "New Issue",
                "description": "Desc",
                "status": "T",
                "priority": "M",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Issue.objects.filter(title="New Issue").exists())

    def test_edit_issue_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/issues/{self.issue.id}/edit/",
            {
                "title": "Updated Issue",
                "description": "Updated",
                "status": "IP",
                "priority": "H",
                "assigned_to": self.other_user.id,
            },
        )
        self.assertEqual(r.status_code, 302)
        self.issue.refresh_from_db()
        self.assertEqual(self.issue.title, "Updated Issue")

    def test_delete_issue_post(self):
        self.client.login(username="alice", password="testpass123")
        issue_id = self.issue.id
        r = self.client.post(f"/issues/{issue_id}/delete/")
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Issue.objects.filter(id=issue_id).exists())

    def test_invite_member_post(self):
        new_user = User.objects.create_user(
            username="charlie", password="testpass123"
        )
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/teams/{self.team.id}/invite/", {"username": "charlie"}
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(
            Membership.objects.filter(
                user=new_user, team=self.team
            ).exists()
        )

    def test_remove_member_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/teams/{self.team.id}/members/{self.other_user.id}/remove/"
        )
        self.assertEqual(r.status_code, 302)
        self.assertFalse(
            Membership.objects.filter(
                user=self.other_user, team=self.team
            ).exists()
        )

    def test_change_member_role_post(self):
        self.client.login(username="alice", password="testpass123")
        r = self.client.post(
            f"/teams/{self.team.id}/members/{self.other_user.id}/role/",
            {"role": "A"},
        )
        self.assertEqual(r.status_code, 302)
        self.other_membership.refresh_from_db()
        self.assertEqual(self.other_membership.role, Membership.Role.ADMIN)

    def test_register_post(self):
        r = self.client.post(
            "/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

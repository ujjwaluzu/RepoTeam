from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='core/login.html'
        ),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("teams/create/", views.create_team, name="create_team"),
    path(
    "teams/<int:team_id>/",
    views.team_detail,
    name="team_detail"
),
path(
    "teams/<int:team_id>/projects/create/",
    views.create_project,
    name="create_project"
),
path(
    "projects/<int:project_id>/",
    views.project_detail,
    name="project_detail"
),
path(
    "projects/<int:project_id>/issues/create/",
    views.create_issue,
    name="create_issue",
),
path(
    "issues/<int:issue_id>/edit/",
    views.edit_issue,
    name="edit_issue",
),
path(
    "issues/<int:issue_id>/delete/",
    views.delete_issue,
    name="delete_issue",
),
path(
    "teams/<int:team_id>/invite/",
    views.invite_member,
    name="invite_member",
),
path(
    "teams/<int:team_id>/members/<int:user_id>/remove/",
    views.remove_member,
    name="remove_member",
),
]


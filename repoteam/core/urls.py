from . import views
from django.urls import path

urlpatterns = [
    path("", views.api_info, name="index"),
    path("api/health/", views.health_api, name="health_api"),
    path("api/auth/me/", views.me_api, name="me_api"),
    path("api/auth/login/", views.login_api, name="login_api"),
    path("api/auth/logout/", views.logout_api, name="logout_api"),
    path("api/auth/register/", views.register_api, name="register_api"),
    path("api/profile/me/", views.my_profile_api, name="my_profile_api"),
    path("api/developers/", views.developers_api, name="developers_api"),
    path("api/developers/<str:username>/", views.developer_detail_api, name="developer_detail_api"),
    path("api/projects/", views.projects_api, name="projects_api"),
    path("api/projects/<slug:slug>/", views.project_detail_api, name="project_detail_api"),
    path("api/projects/<slug:slug>/publish/", views.publish_project_api, name="publish_project_api"),
    path("api/projects/<slug:slug>/archive/", views.archive_project_api, name="archive_project_api"),
]

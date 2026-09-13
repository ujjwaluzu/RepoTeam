from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, TeamForm, ProjectForm, IssueForm, InviteMemberForm
from django.contrib import messages
from .models import Team, Membership, Project, Issue, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Saves the user to the database
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')  # Redirect to your login url
    else:
        form = RegistrationForm()
        
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.is_authenticated:
        memberships = Membership.objects.filter(user=request.user)
        teams = [membership.team for membership in memberships]

        return render(
            request,
            'core/dashboard.html',
            {'teams': teams}
        )
@login_required  
def create_team(request):
    if request.method == "POST":
        form = TeamForm(request.POST)

        if form.is_valid():
            team = form.save(commit=False)
            team.created_by = request.user
            team.save()

            Membership.objects.create(
                user=request.user,
                team=team,
                role=Membership.Role.OWNER
            )

            return redirect("dashboard")

    else:
        form = TeamForm()

    return render(request, "core/create_team.html", {"form": form})

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=team
    ).first()

    if membership is None:
        return redirect("dashboard")

    memberships = Membership.objects.filter(team=team)
    projects = Project.objects.filter(team=team)

    return render(
        request,
        "core/team_detail.html",
        {
            "team": team,
            "membership": membership,
            "memberships": memberships,
            "projects": projects,
        }
    )

@login_required
def create_project(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=team
    ).first()

    if membership is None:
        return redirect("dashboard")

    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.team = team
            project.created_by = request.user
            project.save()

            return redirect("team_detail", team_id=team.id)

    else:
        form = ProjectForm()

    return render(
        request,
        "core/create_project.html",
        {
            "form": form,
            "team": team,
        }
    )


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=project.team
    ).first()

    if membership is None:
        return redirect("dashboard")

    issues = Issue.objects.filter(project=project)

    return render(
        request,
        "core/project_detail.html",
        {
            "project": project,
            "issues": issues,
            "membership": membership,
        }
    )



@login_required
def create_issue(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=project.team,
    ).first()

    if membership is None:
        return redirect("dashboard")

    member_ids = Membership.objects.filter(
        team=project.team
    ).values_list("user_id", flat=True)

    assigned_users = User.objects.filter(
        id__in=member_ids
    )

    if request.method == "POST":
        form = IssueForm(
            request.POST,
            assigned_users=assigned_users,
        )

        if form.is_valid():
            issue = form.save(commit=False)
            issue.project = project
            issue.created_by = request.user
            issue.save()

            messages.success(
                request,
                "Issue created successfully.",
            )

            return redirect(
                "project_detail",
                project_id=project.id,
            )
    else:
        form = IssueForm(
            assigned_users=assigned_users,
        )

    return render(
        request,
        "core/create_issue.html",
        {
            "form": form,
            "project": project,
        },
    )



@login_required
def edit_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=issue.project.team,
    ).first()

    if membership is None:
        return redirect("dashboard")

    member_ids = Membership.objects.filter(
        team=issue.project.team
    ).values_list("user_id", flat=True)

    assigned_users = User.objects.filter(
        id__in=member_ids
    )

    if request.method == "POST":
        form = IssueForm(
            request.POST,
            instance=issue,
            assigned_users=assigned_users,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Issue updated successfully.",
            )

            return redirect(
                "project_detail",
                project_id=issue.project.id,
            )
    else:
        form = IssueForm(
            instance=issue,
            assigned_users=assigned_users,
        )

    return render(
        request,
        "core/edit_issue.html",
        {
            "form": form,
            "issue": issue,
        },
    )

@login_required
def delete_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=issue.project.team,
    ).first()

    if membership is None:
        return redirect("dashboard")

    if request.method == "POST":
        project_id = issue.project.id
        issue.delete()

        messages.success(
            request,
            "Issue deleted successfully.",
        )

        return redirect(
            "project_detail",
            project_id=project_id,
        )

    return render(
        request,
        "core/delete_issue.html",
        {"issue": issue},
    )


@login_required
def invite_member(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=team,
    ).first()

    if membership is None:
        return redirect("dashboard")

    if membership.role not in [
        Membership.Role.OWNER,
        Membership.Role.ADMIN,
    ]:
        messages.error(
            request,
            "Only team owners and admins can invite members.",
        )
        return redirect("team_detail", team_id=team.id)

    if request.method == "POST":
        form = InviteMemberForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]

            invited_user = User.objects.filter(
                username=username
            ).first()

            if invited_user is None:
                form.add_error(
                    "username",
                    "No user exists with that username.",
                )
            elif Membership.objects.filter(
                user=invited_user,
                team=team,
            ).exists():
                form.add_error(
                    "username",
                    "This user is already a team member.",
                )
            else:
                Membership.objects.create(
                    user=invited_user,
                    team=team,
                    role=Membership.Role.MEMBER,
                )

                messages.success(
                    request,
                    f"{username} was added to the team.",
                )

                return redirect(
                    "team_detail",
                    team_id=team.id,
                )
    else:
        form = InviteMemberForm()

    return render(
        request,
        "core/invite_member.html",
        {
            "form": form,
            "team": team,
        },
    )
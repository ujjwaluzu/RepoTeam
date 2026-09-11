from django.shortcuts import render, redirect
from .forms import RegistrationForm, TeamForm
from django.contrib import messages
from .models import Team, Membership, Project, Issue, Comment
from django.shortcuts import render, redirect, get_object_or_404
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


def dashboard(request):
    if request.user.is_authenticated:
        memberships = Membership.objects.filter(user=request.user)
        teams = [membership.team for membership in memberships]

        return render(
            request,
            'core/dashboard.html',
            {'teams': teams}
        )
    
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


def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    membership = Membership.objects.filter(
        user=request.user,
        team=team
    ).first()

    if membership is None:
        return redirect("dashboard")

    memberships = Membership.objects.filter(team=team)

    return render(
        request,
        "core/team_detail.html",
        {
            "team": team,
            "membership": membership,
            "memberships": memberships,
        }
    )
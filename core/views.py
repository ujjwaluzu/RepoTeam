from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib import messages
from .models import Team, Membership, Project, Issue, Comment
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
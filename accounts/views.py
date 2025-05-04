from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from groups.models import Player
from .forms import LoginForm, RegisterForm, UserProfileForm
from .models import User
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    form = LoginForm(data=request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('homepage')
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        return redirect('homepage')
    return render(request, 'accounts/register.html', {'form': form})

# accounts/views.py


@login_required
def become_organizer(request):
    if request.method == 'POST':
        user = request.user
        user.role = 'organizer'
        user.save()
        return redirect('homepage')
    return render(request, 'accounts/become_organizer.html')

@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            # 🔁 Sincronizza nome/cognome/data con i profili Player
            Player.objects.filter(user=user).update(
                name=f"{user.first_name} {user.last_name}".strip(),
                birth_date=user.birth_date
            )
            messages.success(request, "Profilo aggiornato con successo.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=user)

    return render(request, "accounts/profile.html", {"form": form})

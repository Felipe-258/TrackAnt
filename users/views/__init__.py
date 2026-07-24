from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from users.forms import RegistroForm
from users.models import Colony
from .settings import settings_view


def _assign_colony(request, user):
    colony = user.owned_colonies.filter(is_guest=False).first()
    if not colony:
        colony = getattr(request, 'colony', None)
        if colony and colony.is_guest:
            colony.owner = user
            colony.is_guest = False
            colony.name = f'Colonia de {user.username}'
            colony.save()
    if colony:
        request.session['colony_id'] = colony.id
        request.colony = colony


def welcome(request):
    if request.method == 'POST':
        action = request.POST.get('action', 'guest')
        if action == 'guest':
            request.session['welcome_seen'] = True
        return redirect('finances:dashboard')
    return render(request, 'users/welcome.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('finances:dashboard')
    if request.method == 'POST':
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            _assign_colony(request, user)
            request.session['welcome_seen'] = True
            request.session.modified = True
            request.session.save()
            messages.success(request, f'Bienvenido, {user.username}')
            return redirect('finances:dashboard')
    if request.method == 'POST':
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['welcome_seen'] = True
            _assign_colony(request, user)
            request.session.modified = True
            messages.success(request, f'Bienvenido, {user.username}')
            return redirect('finances:dashboard')
    else:
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def registro(request):
    if request.user.is_authenticated:
        return redirect('finances:dashboard')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            _assign_colony(request, user)
            request.session['welcome_seen'] = True
            request.session.modified = True
            request.session.save()
            messages.success(request, f'Colonia creada. Bienvenido, {user.username}')
            return redirect('finances:dashboard')
    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Sesion cerrada')
    return redirect('users:welcome')

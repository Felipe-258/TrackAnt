from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import ColonySettingsForm


def settings_view(request):
    colony = request.colony
    if request.method == 'POST':
        form = ColonySettingsForm(request.POST, instance=colony, colony=colony)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada')
            return redirect('users:settings')
    else:
        form = ColonySettingsForm(instance=colony, colony=colony)
    return render(request, 'users/settings.html', {'form': form})

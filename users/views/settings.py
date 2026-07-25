import shutil
from datetime import timedelta
from pathlib import Path

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from ..forms import ColonySettingsForm


def _get_backup_info():
    backup_dir = Path(settings.DATA_DIR) / 'backups'
    if not backup_dir.exists():
        return None, 0
    backups = sorted(backup_dir.glob('backup_*.sqlite3'), reverse=True)
    last = backups[0].stem.replace('backup_', '').replace('_', ' ') if backups else None
    return last, len(backups)


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
    version = getattr(settings, 'TRACKANT_VERSION', 'dev')
    last_backup, backup_count = _get_backup_info()
    return render(request, 'users/settings.html', {
        'form': form,
        'version': version,
        'last_backup': last_backup,
        'backup_count': backup_count,
    })


@login_required
def backup_download_view(request):
    if request.method != 'POST':
        return redirect('users:settings')

    backup_dir = Path(settings.DATA_DIR) / 'backups'
    backup_dir.mkdir(exist_ok=True)

    timestamp = timezone.now().strftime('%Y-%m-%d_%H%M%S')
    src = Path(settings.DATABASES['default']['NAME'])
    dst = backup_dir / f'backup_{timestamp}.sqlite3'
    shutil.copy2(src, dst)

    cutoff = timezone.now() - timedelta(days=30)
    for f in backup_dir.glob('backup_*.sqlite3'):
        try:
            ts_str = f.stem.replace('backup_', '')
            file_time = timezone.datetime.strptime(ts_str, '%Y-%m-%d_%H%M%S')
            file_time = timezone.make_aware(file_time) if timezone.is_naive(file_time) else file_time
            if file_time < cutoff:
                f.unlink()
        except (ValueError, OSError):
            continue

    messages.success(request, f'Backup creado: {dst.name}')
    response = FileResponse(open(dst, 'rb'), as_attachment=True,
                           filename=f'trackant_backup_{timestamp}.sqlite3')
    return response

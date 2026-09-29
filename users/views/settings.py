import json
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
from ..models import TAB_BAR_DEFAULTS, TAB_ICON_CHOICES, effective_tab_config


def _get_backup_info():
    backup_dir = Path(settings.DATA_DIR) / 'backups'
    if not backup_dir.exists():
        return None, 0
    backups = sorted(backup_dir.glob('backup_*.sqlite3'), reverse=True)
    last = backups[0].stem.replace('backup_', '').replace('_', ' ') if backups else None
    return last, len(backups)


def _save_tab_config(colony, raw):
    if not raw:
        return
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return
    valid_slugs = {t['slug'] for t in TAB_BAR_DEFAULTS}
    cleaned = []
    for item in data:
        if not isinstance(item, dict):
            continue
        slug = item.get('slug')
        if slug in valid_slugs:
            cleaned.append({
                'slug': slug,
                'icon': str(item.get('icon') or ''),
                'label': str(item.get('label') or '').strip(),
                'visible': bool(item.get('visible')),
            })
    colony.tab_bar_config = cleaned
    colony.save(update_fields=['tab_bar_config'])


def settings_view(request):
    colony = request.colony
    if request.method == 'POST':
        form = ColonySettingsForm(request.POST, instance=colony, colony=colony)
        if form.is_valid():
            form.save()
            _save_tab_config(colony, request.POST.get('tab_bar_config', ''))
            messages.success(request, 'Configuración guardada')
            return redirect('users:settings')
    else:
        form = ColonySettingsForm(instance=colony, colony=colony)
    version = getattr(settings, 'TRACKANT_VERSION', 'dev')
    last_backup, backup_count = _get_backup_info()
    tab_config = effective_tab_config(colony)
    editor_tabs = [{k: t[k] for k in ('slug', 'icon', 'label', 'visible')} for t in tab_config]
    return render(request, 'users/settings.html', {
        'form': form,
        'version': version,
        'last_backup': last_backup,
        'backup_count': backup_count,
        'editor_tabs': editor_tabs,
        'tab_icons': TAB_ICON_CHOICES,
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

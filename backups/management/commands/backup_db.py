import shutil
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Crea backup de la DB y limpia backups viejos (>30 días)'

    def handle(self, *args, **options):
        backup_dir = Path(settings.DATA_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)

        src = Path(settings.DATABASES['default']['NAME'])
        if not src.exists():
            self.stderr.write(f'DB no encontrada: {src}')
            return

        timestamp = timezone.now().strftime('%Y-%m-%d_%H%M%S')
        dst = backup_dir / f'backup_{timestamp}.sqlite3'
        shutil.copy2(src, dst)
        self.stdout.write(self.style.SUCCESS(f'Backup creado: {dst.name}'))

        cutoff = timezone.now() - timedelta(days=30)
        deleted = 0
        for f in sorted(backup_dir.glob('backup_*.sqlite3')):
            name = f.stem
            try:
                ts_str = name.replace('backup_', '')
                file_time = timezone.datetime.strptime(ts_str, '%Y-%m-%d_%H%M%S')
                file_time = timezone.make_aware(file_time) if timezone.is_naive(file_time) else file_time
                if file_time < cutoff:
                    f.unlink()
                    deleted += 1
            except (ValueError, OSError):
                continue

        remaining = len(list(backup_dir.glob('backup_*.sqlite3')))
        self.stdout.write(f'Backups eliminados (>30 días): {deleted}')
        self.stdout.write(f'Backups totales: {remaining}')

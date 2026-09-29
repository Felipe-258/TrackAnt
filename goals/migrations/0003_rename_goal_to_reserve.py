import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0002_initial'),
        ('finances', '0010_remove_transaction_is_recurring'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Goal',
            new_name='Reserve',
        ),
        migrations.AlterModelOptions(
            name='reserve',
            options={'ordering': ['-is_achieved', 'deadline', 'name'], 'verbose_name': 'Reserva', 'verbose_name_plural': 'Reservas'},
        ),
        migrations.AlterField(
            model_name='reserve',
            name='target_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Monto objetivo'),
        ),
        migrations.AlterField(
            model_name='reserve',
            name='current_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Saldo actual'),
        ),
    ]

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0010_remove_transaction_is_recurring'),
        ('goals', '0003_rename_goal_to_reserve'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='goal',
            new_name='reserve',
        ),
    ]

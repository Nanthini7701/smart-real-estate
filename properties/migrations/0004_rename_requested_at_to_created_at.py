# Generated manually to rename requested_at to created_at
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_notification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookingrequest',
            old_name='requested_at',
            new_name='created_at',
        ),
    ]

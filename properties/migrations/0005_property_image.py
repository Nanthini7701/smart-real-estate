# Generated manually to add image field to Property
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_rename_requested_at_to_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='image',
            field=models.ImageField(upload_to='property_images/', null=True, blank=True),
        ),
    ]

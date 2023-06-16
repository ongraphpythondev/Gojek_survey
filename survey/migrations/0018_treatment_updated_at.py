# Generated by Django 4.0 on 2023-06-16 06:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0017_participant_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='treatment',
            name='updated_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

# Generated by Django 4.0 on 2023-01-07 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='c0',
            name='participantTypeRequired',
            field=models.CharField(blank=True, default='left', max_length=50),
        ),
    ]

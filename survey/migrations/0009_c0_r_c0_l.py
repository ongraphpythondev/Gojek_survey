# Generated by Django 4.0 on 2023-06-09 07:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0008_treatment'),
    ]

    operations = [
        migrations.CreateModel(
            name='C0_R',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodeID', models.CharField(default=None, max_length=50, null=True, unique=True)),
                ('responseToNews', models.BooleanField(default=None, null=True)),
                ('responseToNewsTimestamp', models.DateTimeField(default=None, null=True)),
                ('status', models.CharField(blank=True, default='outOfService', max_length=50)),
                ('child1ID', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('child2ID', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('participant', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='survey.participant')),
            ],
        ),
        migrations.CreateModel(
            name='C0_L',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nodeID', models.CharField(default=None, max_length=50, null=True, unique=True)),
                ('responseToNews', models.BooleanField(default=None, null=True)),
                ('responseToNewsTimestamp', models.DateTimeField(default=None, null=True)),
                ('status', models.CharField(blank=True, default='outOfService', max_length=50)),
                ('child1ID', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('child2ID', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('participant', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='survey.participant')),
            ],
        ),
    ]

# Generated by Django 4.0 on 2023-06-13 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0010_alter_participant_democaticopinions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t1_l',
            name='nodeID',
            field=models.CharField(default=None, max_length=100, null=True, unique=True),
        ),
    ]

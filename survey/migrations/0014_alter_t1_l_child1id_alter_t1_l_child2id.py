# Generated by Django 4.0 on 2023-06-13 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_alter_t1_l_nodeid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='t1_l',
            name='child1ID',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='t1_l',
            name='child2ID',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
    ]

# Generated by Django 4.0 on 2023-06-14 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0015_remove_democraticopinion2_sources_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='everything',
            name='sources',
        ),
        migrations.AddField(
            model_name='everything',
            name='source_news_channels',
            field=models.CharField(default='', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='everything',
            name='source_newspapers',
            field=models.CharField(default='', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='everything',
            name='source_online_news_blogs',
            field=models.CharField(default='', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='everything',
            name='source_social_media',
            field=models.CharField(default='', max_length=150, null=True),
        ),
    ]
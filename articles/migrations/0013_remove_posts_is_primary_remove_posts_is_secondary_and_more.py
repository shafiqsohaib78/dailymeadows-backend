# Generated by Django 4.2 on 2023-12-28 10:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0012_remove_posts_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='is_primary',
        ),
        migrations.RemoveField(
            model_name='posts',
            name='is_secondary',
        ),
        migrations.RemoveField(
            model_name='posts',
            name='suspended',
        ),
    ]
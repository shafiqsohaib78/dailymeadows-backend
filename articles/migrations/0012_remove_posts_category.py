# Generated by Django 4.2 on 2023-12-28 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_categoryposts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='posts',
            name='category',
        ),
    ]
# Generated by Django 4.2 on 2023-12-28 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0015_remove_paidview_submited'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReadMinutesOfPosts',
        ),
    ]

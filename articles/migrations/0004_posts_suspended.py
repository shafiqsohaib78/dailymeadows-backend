# Generated by Django 4.2 on 2023-07-07 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0003_alter_draftposts_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='suspended',
            field=models.BooleanField(default=False),
        ),
    ]
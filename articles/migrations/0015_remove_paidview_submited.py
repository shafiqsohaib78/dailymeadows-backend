# Generated by Django 4.2 on 2023-12-28 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0014_readminutesofposts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paidview',
            name='submited',
        ),
    ]
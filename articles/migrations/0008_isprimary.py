# Generated by Django 4.2 on 2023-07-07 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0007_suspendedpost'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsPrimary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.posts')),
            ],
        ),
    ]
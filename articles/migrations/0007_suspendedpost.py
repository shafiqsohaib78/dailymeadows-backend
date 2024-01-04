# Generated by Django 4.2 on 2023-07-07 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_posts_read_min'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuspendedPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.posts')),
            ],
        ),
    ]
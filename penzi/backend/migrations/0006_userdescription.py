# Generated by Django 4.2.7 on 2023-11-16 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_alter_userdetails_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description_text', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='description', to='backend.user')),
            ],
        ),
    ]

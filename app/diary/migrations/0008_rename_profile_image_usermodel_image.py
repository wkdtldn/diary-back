# Generated by Django 5.1.1 on 2024-10-12 05:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0007_remove_usermodel_image_usermodel_profile_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usermodel',
            old_name='profile_image',
            new_name='image',
        ),
    ]

# Generated by Django 5.1.1 on 2024-10-19 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0016_alter_usermodel_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermodel',
            name='image',
            field=models.ImageField(default='profile_images/default.jpg', upload_to='profile_images/'),
        ),
    ]

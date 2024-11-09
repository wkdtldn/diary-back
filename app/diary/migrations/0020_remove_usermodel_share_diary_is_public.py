# Generated by Django 5.0.7 on 2024-10-22 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0019_usermodel_share'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermodel',
            name='share',
        ),
        migrations.AddField(
            model_name='diary',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]

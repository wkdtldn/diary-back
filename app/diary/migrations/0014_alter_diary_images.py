# Generated by Django 5.1.1 on 2024-10-19 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0013_alter_diary_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diary',
            name='images',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
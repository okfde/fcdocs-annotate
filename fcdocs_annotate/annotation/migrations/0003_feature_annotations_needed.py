# Generated by Django 3.2.12 on 2022-04-04 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fcdocs_annotation', '0002_rename_describtion_feature_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='documents_needed',
            field=models.PositiveIntegerField(default=10),
        ),
    ]
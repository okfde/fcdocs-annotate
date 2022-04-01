# Generated by Django 3.2.12 on 2022-03-02 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.FILINGCABINET_DOCUMENT_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('question', models.CharField(max_length=500)),
                ('describtion', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FeatureAnnotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('features', models.JSONField(default=dict)),
                ('type', models.CharField(choices=[('TM', 'Manual Annotation'), ('TA', 'Automated Annotations')], default='TM', max_length=2)),
                ('final', models.BooleanField(default=False)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.FILINGCABINET_DOCUMENT_MODEL)),
            ],
        ),
    ]
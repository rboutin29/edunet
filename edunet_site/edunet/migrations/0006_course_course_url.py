# Generated by Django 3.0.8 on 2020-08-03 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edunet', '0005_auto_20200731_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_url',
            field=models.URLField(default='Course URL', max_length=150),
        ),
    ]

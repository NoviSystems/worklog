# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-31 17:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worklog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
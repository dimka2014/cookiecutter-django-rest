# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 22:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_password_token',
            field=models.CharField(blank=True, default=None, max_length=32, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2022-10-28 02:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons_microsoftteams', '0002_auto_20221027_0604'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendees',
            name='has_grdm_account',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='attendees',
            name='is_guest',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='attendees',
            unique_together=set([('email_address', 'node_settings', 'external_account', 'has_grdm_account')]),
        ),
    ]

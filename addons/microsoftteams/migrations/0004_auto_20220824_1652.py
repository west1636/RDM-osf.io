# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2022-08-24 16:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('addons_microsoftteams', '0003_microsoftteams_app_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendees',
            old_name='microsoft_teams_user_name',
            new_name='display_name',
        ),
        migrations.RenameField(
            model_name='attendees',
            old_name='microsoft_teams_mail',
            new_name='email_address',
        ),
        migrations.AlterUniqueTogether(
            name='attendees',
            unique_together=set([('email_address', 'node_settings'), ('user_guid', 'node_settings')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2022-08-28 22:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0221_ensure_schema_and_reports'),
        ('addons_webexmeetings', '0004_auto_20220824_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendees',
            name='external_account',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='webexmeetings_attendees', to='osf.ExternalAccount'),
        ),
        migrations.AlterField(
            model_name='webexmeetings',
            name='external_account',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='webexmeetings_meetings', to='osf.ExternalAccount'),
        ),
    ]

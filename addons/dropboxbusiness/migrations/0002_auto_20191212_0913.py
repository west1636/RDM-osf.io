# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-12-12 09:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0175_auto_20191128_0921'),
        ('addons_dropboxbusiness', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nodesettings',
            name='_admin_dbmid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='nodesettings',
            name='fileaccess_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dropboxbusiness_fileaccess_node_settings', to='osf.ExternalAccount'),
        ),
        migrations.AddField(
            model_name='nodesettings',
            name='list_cursor',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='nodesettings',
            name='management_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dropboxbusiness_management_node_settings', to='osf.ExternalAccount'),
        ),
    ]
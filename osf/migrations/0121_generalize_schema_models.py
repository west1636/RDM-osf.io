# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-23 20:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0120_merge_20180716_1457'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MetaSchema',
            new_name='RegistrationSchema',
        ),
    ]

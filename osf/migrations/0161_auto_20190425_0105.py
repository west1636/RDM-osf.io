# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-04-25 01:05
from __future__ import unicode_literals

from django.db import migrations
from osf.utils.migrations import ensure_schemas


class Migration(migrations.Migration):
    dependencies = [
        ('osf', '0160_merge_20190408_1618'),
    ]

    operations = [
        # To reverse this migrations simply revert changes to the schema and re-run
        migrations.RunPython(ensure_schemas, ensure_schemas),
    ]

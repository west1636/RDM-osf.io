# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2023-07-17 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons_wiki', '0012_rename_deleted_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='wikipage',
            name='parent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

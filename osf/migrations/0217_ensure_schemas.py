# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from osf.utils.migrations import UpdateRegistrationSchemasAndSchemaBlocks


def ensure_registration_reports(*args):
    from addons.metadata.utils import ensure_registration_report
    from addons.metadata.report_format import REPORT_FORMATS
    for schema_name, report_name, csv_template in REPORT_FORMATS:
        ensure_registration_report(schema_name, report_name, csv_template)

def noop(*args):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('osf', '0216_merge_20211009_0007'),
    ]

    operations = [
        UpdateRegistrationSchemasAndSchemaBlocks(),
        migrations.RunPython(ensure_registration_reports, noop),
    ]

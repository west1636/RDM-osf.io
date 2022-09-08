# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2022-09-08 13:31
from __future__ import unicode_literals

import addons.base.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import osf.models.base
import osf.utils.datetime_aware_jsonfield
import osf.utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('osf', '0221_ensure_schema_and_reports'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('_id', models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True)),
                ('user_guid', models.CharField(default=None, max_length=255)),
                ('fullname', models.CharField(max_length=255)),
                ('email_address', models.CharField(blank=True, max_length=254, null=True)),
                ('display_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_guest', models.BooleanField(default=False)),
                ('external_account', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='microsoftteams_attendees', to='osf.ExternalAccount')),
            ],
            bases=(models.Model, osf.models.base.QuerySetExplainMixin),
        ),
        migrations.CreateModel(
            name='Meetings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('_id', models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True)),
                ('subject', models.CharField(max_length=255)),
                ('organizer', models.CharField(max_length=255)),
                ('organizer_fullname', models.CharField(max_length=255)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('content', models.TextField(blank=True, max_length=10000, null=True)),
                ('join_url', models.TextField(max_length=512)),
                ('meetingid', models.TextField(max_length=512)),
                ('app_name', models.CharField(default='Microsoft Teams', max_length=128)),
                ('attendees', models.ManyToManyField(related_name='attendees_meetings', to='addons_microsoftteams.Attendees')),
                ('external_account', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='microsoftteams_meetings', to='osf.ExternalAccount')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, osf.models.base.QuerySetExplainMixin),
        ),
        migrations.CreateModel(
            name='NodeSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('_id', models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted', osf.utils.fields.NonNaiveDateTimeField(blank=True, null=True)),
                ('folder_id', models.TextField(blank=True, null=True)),
                ('folder_name', models.TextField(blank=True, null=True)),
                ('folder_location', models.TextField(blank=True, null=True)),
                ('external_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_microsoftteams_node_settings', to='osf.ExternalAccount')),
                ('owner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_microsoftteams_node_settings', to='osf.AbstractNode')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, osf.models.base.QuerySetExplainMixin, addons.base.models.BaseStorageAddon),
        ),
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('_id', models.CharField(db_index=True, default=osf.models.base.generate_object_id, max_length=24, unique=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted', osf.utils.fields.NonNaiveDateTimeField(blank=True, null=True)),
                ('oauth_grants', osf.utils.datetime_aware_jsonfield.DateTimeAwareJSONField(blank=True, default=dict, encoder=osf.utils.datetime_aware_jsonfield.DateTimeAwareJSONEncoder)),
                ('owner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addons_microsoftteams_user_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, osf.models.base.QuerySetExplainMixin),
        ),
        migrations.AddField(
            model_name='nodesettings',
            name='user_settings',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='addons_microsoftteams.UserSettings'),
        ),
        migrations.AddField(
            model_name='meetings',
            name='node_settings',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='addons_microsoftteams.NodeSettings'),
        ),
        migrations.AddField(
            model_name='attendees',
            name='node_settings',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='addons_microsoftteams.NodeSettings'),
        ),
        migrations.AlterUniqueTogether(
            name='attendees',
            unique_together=set([('email_address', 'node_settings', 'is_guest')]),
        ),
    ]

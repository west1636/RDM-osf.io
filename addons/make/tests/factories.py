# -*- coding: utf-8 -*-
"""Factories for the Make addon."""
import factory
from datetime import date, datetime, timedelta
from factory.django import DjangoModelFactory
from osf.models.user import OSFUser

from addons.make import SHORT_NAME
from addons.make.models import (
    UserSettings,
    NodeSettings,
    WorkflowExecutionMessages,
    Attendees,
    NodeFileWebappMap
)

from osf_tests.factories import UserFactory, ProjectFactory, ExternalAccountFactory

class MakeAccountFactory(ExternalAccountFactory):
    provider = SHORT_NAME
    provider_id = factory.Sequence(lambda n: 'id-{0}'.format(n))
    oauth_key = factory.Sequence(lambda n: 'key-{0}'.format(n))
    display_name = 'Make Fake User'


class MakeUserSettingsFactory(DjangoModelFactory):
    class Meta:
        model = UserSettings

    owner = factory.SubFactory(UserFactory)


class MakeNodeSettingsFactory(DjangoModelFactory):
    class Meta:
        model = NodeSettings

    _id = 'qwe'
    owner = factory.SubFactory(ProjectFactory)
    user_settings = factory.SubFactory(MakeUserSettingsFactory)


class MakeWorkflowExecutionMessagesFactory(DjangoModelFactory):
    class Meta:
        model = WorkflowExecutionMessages

    notified = False
    make_msg = 'make.info.message'
    timestamp = '1234567890123'
    node_settings = factory.SubFactory(MakeNodeSettingsFactory)

class MakeAttendeesFactory(DjangoModelFactory):
    class Meta:
        model = Attendees

    _id = '1234567890qwertyuiop'
    user_guid = 'testuser'
    fullname = 'TEST USER'
    microsoft_teams_mail = 'testUser1@test.onmicrosoft.com'
    microsoft_teams_user_name = 'Teams User'
    webex_meetings_mail = 'testUser2@test.co.jp'
    webex_meetings_display_name = 'Webex User'
    zoom_meetings_mail = 'testUser3@test.co.jp'
    is_guest = False
    node_settings = factory.SubFactory(MakeNodeSettingsFactory)

class MakeNodeFileWebappMapFactory(DjangoModelFactory):
    class Meta:
        model = NodeFileWebappMap

    node_file_guid = 'xyz89'
    slack_channel_id = 'ABCDE987654321'

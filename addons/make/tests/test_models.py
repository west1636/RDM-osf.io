# from nose.tools import *  # noqa
import unittest
import json
import mock
import pytest
from nose.tools import (assert_false, assert_true,
                        assert_equal, assert_is_none)

from addons.base.tests.models import (
    OAuthAddonNodeSettingsTestSuiteMixin,
    OAuthAddonUserSettingTestSuiteMixin
)
from addons.make import SHORT_NAME, FULL_NAME
from addons.make import settings
from addons.make.models import NodeSettings, Attendees
from addons.make.tests.factories import (
    MakeUserSettingsFactory,
    MakeNodeSettingsFactory,
    MakeAccountFactory,
    MakeAttendeesFactory
)
from framework.auth import Auth
from osf_tests.factories import ProjectFactory, DraftRegistrationFactory
from tests.base import get_default_metaschema
from django.core import serializers
pytestmark = pytest.mark.django_db

import logging
logger = logging.getLogger(__name__)

from addons.make.models import (
    UserSettings,
    NodeSettings,
    WorkflowExecutionMessages,
    Attendees,
    AllMeetingInformation,
    AllMeetingInformationAttendeesRelation,
    NodeWorkflows
)

class TestUserSettings(OAuthAddonUserSettingTestSuiteMixin, unittest.TestCase):

    short_name = SHORT_NAME
    full_name = FULL_NAME
    ExternalAccountFactory = MakeAccountFactory


class TestNodeSettings(OAuthAddonNodeSettingsTestSuiteMixin, unittest.TestCase):

    short_name = SHORT_NAME
    full_name = FULL_NAME
    ExternalAccountFactory = MakeAccountFactory
    NodeSettingsFactory = MakeNodeSettingsFactory
    NodeSettingsClass = NodeSettings
    UserSettingsFactory = MakeUserSettingsFactory

    def test_registration_settings(self):
        registration = ProjectFactory()
        clone, message = self.node_settings.after_register(
            self.node, registration, self.user,
        )
        assert_is_none(clone)

    def test_before_register_no_settings(self):
        self.node_settings.user_settings = None
        message = self.node_settings.before_register(self.node, self.user)
        assert_false(message)

    def test_before_register_no_auth(self):
        self.node_settings.external_account = None
        message = self.node_settings.before_register(self.node, self.user)
        assert_false(message)

    def test_before_register_settings_and_auth(self):
        message = self.node_settings.before_register(self.node, self.user)
        assert_true(message)

    ## Overrides ##

    def test_set_folder(self):
        pass

    def test_serialize_credentials(self):
        pass

    def test_serialize_credentials_not_authorized(self):
        pass

    def test_serialize_settings(self):
        pass

    def test_serialize_settings_not_configured(self):
        pass

    def test_create_log(self):
        pass


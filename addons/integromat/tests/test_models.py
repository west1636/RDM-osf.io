from nose.tools import assert_is_not_none, assert_equal
import pytest
import unittest

from addons.base.tests.models import (OAuthAddonNodeSettingsTestSuiteMixin,
                                      OAuthAddonUserSettingTestSuiteMixin)

from addons.intgromat.models import NodeSettings
from addons.integromat.tests.factories import (
    IntegromatAccountFactory, IntegromatNodeSettingsFactory,
    IntegromatUserSettingsFactory
)
from addons.integromat.settings import USE_SSL

pytestmark = pytest.mark.django_db

class TestUserSettings(OAuthAddonUserSettingTestSuiteMixin, unittest.TestCase):

    short_name = 'integromat'
    full_name = 'Integromat'
    UserSettingsFactory = IntegromatUserSettingsFactory
    ExternalAccountFactory = IntegromatAccountFactory


class TestNodeSettings(OAuthAddonNodeSettingsTestSuiteMixin, unittest.TestCase):

    short_name = 'integromat'
    full_name = 'Integromat'
    ExternalAccountFactory = IntegromatAccountFactory
    NodeSettingsFactory = IntegromatNodeSettingsFactory
    NodeSettingsClass = NodeSettings
    UserSettingsFactory = IntegromatUserSettingsFactory

    def _node_settings_class_kwargs(self, node, user_settings):
        return {
            'user_settings': self.user_settings,
            'owner': self.node
        }

    def test_serialize_settings(self):

        settings = self.node_settings.serialize_waterbutler_settings()
        expected = {'owner': self.node_settings.user}
        assert_equal(settings, expected)

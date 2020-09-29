# -*- coding: utf-8 -*-
"""Serializer tests for the Integromat addon."""
import mock
import pytest

from tests.base import OsfTestCase
from addons.base.tests.serializers import OAuthAddonSerializerTestSuiteMixin
from addons.integromat.tests.factories import IntegromatAccountFactory
from addons.integromat.serializer import IntegromatSerializer

pytestmark = pytest.mark.django_db

class TestIntegromatSerializer(OAuthAddonSerializerTestSuiteMixin, OsfTestCase):

    addon_short_name = 'integromat'

    Serializer = IntegromatSerializer
    ExternalAccountFactory = IntegromatAccountFactory

    ## Overrides ##

    def setUp(self):
        super(TestIntegromatSerializer, self).setUp()
        self.mock_api_user = mock.patch('addons.integromat.views.authIntegromat')
        self.mock_api_user.return_value = True
        self.mock_api_user.start()

    def tearDown(self):
        self.mock_api_user.stop()
        super(TestIntegromatSerializer, self).tearDown()

    def test_serialize_acccount(self):
        ea = self.ExternalAccountFactory()
        expected = {
            'id': ea._id,
            'provider_id': ea.provider_id,
            'provider_name': ea.provider_name,
            'provider_short_name': ea.provider,
            'display_name': ea.display_name,
            'profile_url': ea.profile_url,
            'nodes': [],
        }
        assert self.ser.serialize_account(ea) == expected

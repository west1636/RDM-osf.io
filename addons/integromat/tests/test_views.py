# -*- coding: utf-8 -*-
import httplib as http

import mock
import datetime
import pytest
import unittest
from json import dumps

from tests.base import OsfTestCase
from osf_tests.factories import InstitutionFactory

from addons.base.tests.views import OAuthAddonConfigViewsTestCaseMixin
from addons.integromat.serializer import IntegromatSerializer
from addons.integromat.tests.utils import IntegromatAddonTestCase
from addons.integromat.tests.factories import IntegromatAccountFactory
from admin.rdm_addons.utils import get_rdm_addon_option

pytestmark = pytest.mark.django_db

class TestIntegromatConfigViews(IntegromatAddonTestCase, OAuthAddonConfigViewsTestCaseMixin, OsfTestCase):
    folder = None
    Serializer = IntegromatSerializer

    ## Overrides ##

    def setUp(self):
        super(TestIntegromatSerializer, self).setUp()
        self.mock_api_user = mock.patch('addons.integromat.views.authIntegromat')
        self.mock_api_user.return_value = True
        self.mock_api_user.start()

    def tearDown(self):
        self.mock_api_user.stop()
        super(TestIntegromatSerializer, self).tearDown()

    def test_get_config(self):
        url = self.project.api_url_for(
            '{0}_get_config'.format(self.ADDON_SHORT_NAME))
        res = self.app.get(url, auth=self.user.auth)
        assert_equal(res.status_code, http.OK)
        assert_in('result', res.json)
        serialized = self.Serializer().serialize_settings(
            self.node_settings,
            self.user,
        )
        assert_equal(serialized, res.json['result'])

    def test_add_user_account_rdm_addons_denied(self):
        institution = InstitutionFactory()
        self.user.affiliated_institutions.add(institution)
        self.user.save()
        rdm_addon_option = get_rdm_addon_option(institution.id, self.ADDON_SHORT_NAME)
        rdm_addon_option.is_allowed = False
        rdm_addon_option.save()
        url = self.project.api_url_for('integromat_add_user_account')
        rv = self.app.post_json(url,{
            'oauth_key': 'aldkjf',
            'provider_id': 'https://hook.integromat.com/6cv9g'
        }, auth=self.user.auth, expect_errors=True)
        assert_equal(rv.status_int, http.FORBIDDEN)
        assert_in('You are prohibited from using this add-on.', rv.body)

# -*- coding: utf-8 -*-
import mock
import pytest
import json
from tests.base import OsfTestCase
from osf_tests.factories import AuthUserFactory, ProjectFactory
from framework.auth import Auth
from .user_attribute_utils import MockResponse, mock_response, mock_data
from website.util import api_url_for, web_url_for


class TestViews(OsfTestCase):
    def setUp(self):
        super(TestViews, self).setUp()
        self.user = AuthUserFactory()
        self.user_addon = self.user.get_addon('xattr')
        self.user_settings = self.user.get_addon('xattr')
        self.auth = Auth(user=self.user)

    @mock.patch('website.profile.views.api_user_attribute_get')
    def test_get_edit_page(self, mock_userget):
        mock_userget.return_value = mock_response['userAttribute']

        url = web_url_for('user_attribute', uid=self.user._id)
        response = self.app.get(url, auth=self.user.auth)
        assert response.status_code == 200
        assert 'Tanaka Taro' in response.text

    @mock.patch('website.profile.views.api_user_attribute_put')
    def test_post_attributes(self, mock_userpost):
        mock_userpost.return_value = mock_response['userAttribute']

        url = api_url_for('user_attribute_post', uid=self.user._id)
        response = self.app.post_json(url, {
            'userAttribute': mock_data['userAttribute'],
        }, auth=self.user.auth)
        assert response.status_code == 200
        assert response.json['status'] == 'OK'

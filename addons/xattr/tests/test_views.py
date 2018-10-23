# coding:utf-8
import mock
import pytest
import json
from tests.base import OsfTestCase
from osf_tests.factories import AuthUserFactory, ProjectFactory
from framework.auth import Auth
from .utils import MockResponse, mock_response, mock_data


class TestViews(OsfTestCase):
    def setUp(self):
        super(TestViews, self).setUp()
        self.user = AuthUserFactory()
        self.user_addon = self.user.get_addon('xattr')
        self.user_settings = self.user.get_addon('xattr')
        self.auth = Auth(user=self.user)
        self.project = ProjectFactory(creator=self.user)

    @mock.patch('addons.xattr.views.api_contributor_get')
    @mock.patch('addons.xattr.views.api_funding_get')
    @mock.patch('addons.xattr.views.api_project_get')
    @mock.patch('addons.xattr.views.api_commonmaster_get')
    def test_get_empty_edit_page(self, mock_comm, mock_proj, mock_fund, mock_cont):
        mock_comm.return_value = [{ 'name': 'Mocked option' }]
        mock_proj.return_value = MockResponse({'data': None}, 200)
        mock_fund.return_value = MockResponse({'data': None}, 200)
        mock_cont.return_value = MockResponse({'data': {}}, 200)

        url = self.project.web_url_for('get_attributes')
        response = self.app.get(url, auth=self.user.auth)

        mock_comm.assert_called()
        mock_proj.assert_called_once_with(self.project._id)
        mock_fund.assert_called_once_with(self.project._id)
        mock_cont.assert_called_once_with(self.project._id)
        assert response.status_code == 200
        assert 'Mocked option' in response.text


    @mock.patch('addons.xattr.views.api_contributor_get')
    @mock.patch('addons.xattr.views.api_funding_get')
    @mock.patch('addons.xattr.views.api_project_get')
    @mock.patch('addons.xattr.views.api_commonmaster_get')
    def test_get_filled_edit_page(self, mock_comm, mock_proj, mock_fund, mock_cont):
        mock_comm.return_value = [{ 'name': 'Mocked option' }]
        mock_proj.return_value = mock_response['project']
        mock_fund.return_value = mock_response['funding']
        mock_cont.return_value = mock_response['contributor']

        url = self.project.web_url_for('get_attributes')
        response = self.app.get(url, auth=self.user.auth)

        mock_comm.assert_called()
        mock_proj.assert_called_once_with(self.project._id)
        mock_fund.assert_called_once_with(self.project._id)
        mock_cont.assert_called_once_with(self.project._id)
        assert response.status_code == 200
        assert 'Mocked option' in response.text
        assert 'Mock Project Title' in response.text
        assert 'Money Tree' in response.text
        assert 'John Contributor' in response.text


    @mock.patch('addons.xattr.views.api_contributor_put')
    @mock.patch('addons.xattr.views.api_funding_put')
    @mock.patch('addons.xattr.views.api_project_put')
    def test_post_attributes_success(self, mock_proj, mock_fund, mock_cont):
        mock_proj.return_value = MockResponse(None, 200)
        mock_fund.return_value = MockResponse(None, 200)
        mock_cont.return_value = MockResponse(None, 200)

        url = self.project.api_url_for('api_post_attributes')
        response = self.app.post_json(url, {
            'projectAttribute': mock_data['project'],
            'fundingAttribute': mock_data['funding'],
            'contributorAttribute': mock_data['contributor']
        }, auth=self.user.auth)

        mock_proj.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['project'])),
            'user_id': self.user.id,
            'status_id': 1
        })
        mock_fund.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['funding'])),
            'user_id': self.user.id
        })
        mock_cont.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['contributor'])),
            'user_id': self.user.id
        })
        assert response.status_code == 200
        assert response.json['Status'] == 'OK'


    @mock.patch('addons.xattr.views.api_contributor_put')
    @mock.patch('addons.xattr.views.api_funding_put')
    @mock.patch('addons.xattr.views.api_project_put')
    def test_post_attributes_fail(self, mock_proj, mock_fund, mock_cont):
        mock_proj.return_value = MockResponse(None, 400)
        mock_fund.return_value = MockResponse(None, 200)
        mock_cont.return_value = MockResponse(None, 200)

        url = self.project.api_url_for('api_post_attributes')
        response = self.app.post_json(url, {
            'projectAttribute': mock_data['project'],
            'fundingAttribute': mock_data['funding'],
            'contributorAttribute': mock_data['contributor']
        }, auth=self.user.auth)

        mock_proj.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['project'])),
            'user_id': self.user.id,
            'status_id': 1
        })
        mock_fund.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['funding'])),
            'user_id': self.user.id
        })
        mock_cont.assert_called_once_with(self.project._id, {
            'content': json.loads(json.dumps(mock_data['contributor'])),
            'user_id': self.user.id
        })
        assert response.status_code == 200
        assert response.json['Status'] == 'Failed'

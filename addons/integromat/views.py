# -*- coding: utf-8 -*-
from flask import request
import logging
import requests

from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.integromat.serializer import IntegromatSerializer
#from addons.integromat.apps import IntegromatSerializer
from osf.models import ExternalAccount
from django.core.exceptions import ValidationError
from framework.exceptions import HTTPError
from rest_framework import status as http_status
from website.util import api_url_for
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
)
from website.ember_osf_web.views import use_ember_app
from website.project import views as project_views
from osf.models.licenses import serialize_node_license_record
from framework.utils import iso8601format
from website.project.model import has_anonymous_link
from django.apps import apps
from osf.utils.permissions import ADMIN, READ, WRITE
from website import settings
from osf.models import Node
from website.project.metadata.utils import serialize_meta_schemas
from website.profile import utils

logger = logging.getLogger(__name__)

SHORT_NAME = 'integromat'
FULL_NAME = 'Integromat'


integromat_account_list = generic_views.account_list(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_get_config = generic_views.get_config(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_import_auth = generic_views.import_auth(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
def integromat_user_config_get(auth, **kwargs):
    """View for getting a JSON representation of the logged-in user's
    Integromat user settings.
    """

    user_addon = auth.user.get_addon('integromat')
    user_has_auth = False
    if user_addon:
        user_has_auth = user_addon.has_auth

    return {
        'result': {
            'userHasAuth': user_has_auth,
            'urls': {
                'create': api_url_for('integromat_add_user_account'),
                'accounts': api_url_for('integromat_account_list'),
            },
        },
    }, http_status.HTTP_200_OK

@must_be_logged_in
def integromat_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    hSdkVersion = '2.0.0'
    try:
        access_token = request.json.get('integromat_api_token')
        webhook_url = request.json.get('integromat_webhook_url')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    if not authIntegromat(access_token, hSdkVersion):
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    try:
#        integromatUserInfo = getIntegromatUser(access_token, hSdkVersion)
    except ValidationError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

#    integromat_userid = integromatUserInfo['id']
#    integromat_username = integromatUserInfo['name']
    user = auth.user

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name='testname',
            oauth_key=access_token,
            provider_id='testid',
            webhook_url=webhook_url,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id='testid'
        )
        if account.oauth_key != access_token:
            account.oauth_key = access_token
            account.save()

        if account.webhook_url != webhook_url:
            account.webhook_url = webhook_url
            account.save()

    if not user.external_accounts.filter(id=account.id).exists():

        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    return {}

def authIntegromat(access_token, hSdkVersion):

    integromatApiUrl = 'https://api.integromat.com/v1/app'
    authSuccess = False
    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request('GET', integromatApiUrl, headers=headers, data=payload)
    authJson = response.json()

    if not type(authJson) is dict:
        authSuccess = True

    return authSuccess

def getIntegromatUser(access_token, hSdkVersion):

    integromatApiWhoami = 'https://api.integromat.com/v1/whoami'
    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request('GET', integromatApiWhoami, headers=headers, data=payload)
    userInfo = response.json()

    return userInfo


# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_integromat(**kwargs):
    return use_ember_app()

@must_be_valid_project
#@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def integromat_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    return {'data': {'id': node._id, 'type': 'integromat-config',
                     'attributes': {
                         'webhook_url': addon.external_account.webhook_url
                     }}}

def integromat_api_call(**kwargs):

    logger.info('integromat called integromat_api_call')

    return {}
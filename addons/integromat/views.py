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
from rest_framework import status as http_status

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

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    if not authIntegromat(access_token, hSdkVersion):
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    user = auth.user

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name=user.username,
            oauth_key=access_token,
            provider_id=access_token,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id=access_token
        )
        if account.oauth_key != access_token:
            account.oauth_key = access_token
            account.save()

    if not user.external_accounts.filter(id=account.id).exists():

        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    return {}

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

def authIntegromat(access_token, hSdkVersion):

    integromatApiUrl = "https://api.integromat.com/v1/app"

    payload = {}
    headers = {
        'Authorization': access_token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response=requests.request("GET", integromatApiUrl, headers=headers, data = payload)

    logger.info('integromatLog1::headers' + str(headers))
    logger.info('integromatLog2::' + str(response.text.encode('utf8')))

    return False

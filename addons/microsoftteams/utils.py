# -*- coding: utf-8 -*-
import json
import requests
from osf.models import ExternalAccount
from addons.microsoftteams import models
from addons.microsoftteams import settings
from django.core import serializers
import logging
from datetime import timedelta
import dateutil.parser
from django.db import transaction
logger = logging.getLogger(__name__)

# widget: ここから
def serialize_microsoftteams_widget(node):
    microsoftteams = node.get_addon('microsoftteams')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': microsoftteams.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(microsoftteams.config.to_json())
    return ret
# widget: ここまで

def get_organization_info(microsoftteams_tenant, access_token):

    url = settings.MICROSOFT_GRAPH_API_URL_ORGANIZATION
    payload = {}
    token = 'Bearer ' + access_token
    requestHeaders = {
        'Authorization': token,
    }

    response = requests.request('GET', url, headers=requestHeaders, data=payload)
    status_code = response.status_code
    responseData = response.json()
    organizationInfo = {}

    logger.info(str(responseData))
    logger.info(str(status_code))

    if status_code != 200:
        if status_code == 401:
            logger.info('Failed to authenticate Microsoft 365 account' + '[' + str(status_code) + ']' + ':' + response.message)
    else:
        organizationInfo['id'] = microsoftteams_tenant
        organizationInfo['displayName'] = responseData['value']['displayName']

    return organizationInfo

def get_access_token(microsoftteams_tenant, microsoftteams_client_id, microsoftteams_client_secret):

    url = settings.MICROSOFT_ONLINE_BASE_URL + microsoftteams_tenant + '/oauth2/v2.0/token'
    payload = {
        'client_id': microsoftteams_client_id,
        'client_secret': microsoftteams_client_secret,
        'grant_type':'client_credentials',
        'scope': settings.MICROSOFT_GRAPH_DEFAULT_SCOPE,
    }

    response = requests.request('POST', url, data=payload)
    status_code = response.status_code
    responseData = response.json()
    accessToken = ''

    logger.info(str(responseData))
    logger.info(str(status_code))

    if status_code != 200:
        if status_code == 400:
            logger.info('Failed to authenticate Microsoft 365 account' + '[' + str(status_code) + ']' + ':' + response.message)
    else:
        accessToken = responseData['access_token']

    return accessToken


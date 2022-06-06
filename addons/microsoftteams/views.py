# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.microsoftteams import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.microsoftteams.serializer import MicrosoftTeamsSerializer
from osf.models import ExternalAccount, OSFUser
from django.core.exceptions import ValidationError
from framework.exceptions import HTTPError
from rest_framework import status as http_status
from osf.utils.permissions import ADMIN, WRITE, READ
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from admin.rdm_addons.decorators import must_be_rdm_addons_allowed
from website.ember_osf_web.views import use_ember_app
from api.base.utils import waterbutler_api_url_for
from addons.microsoftteams import settings
from addons.microsoftteams import models
from addons.microsoftteams import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from osf.models import AbstractNode, BaseFileNode, Guid, Comment
logger = logging.getLogger(__name__)

microsoftteams_account_list = generic_views.account_list(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_get_config = generic_views.get_config(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_import_auth = generic_views.import_auth(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def microsoftteams_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    try:
        microsoftteams_tenant = request.json.get('microsoftteams_tenant')
        microsoftteams_client_id = request.json.get('microsoftteams_client_id')
        microsoftteams_client_secret = request.json.get('microsoftteams_client_secret')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    if not (microsoftteams_tenant and microsoftteams_client_id and microsoftteams_client_secret):
        return {
            'message': 'All the fields above are required.'
        }, http_status.HTTP_400_BAD_REQUEST

    access_token = utils.get_access_token(microsoftteams_tenant, microsoftteams_client_id, microsoftteams_client_secret)
    if not access_token:
        return {
            'message': ('Unable to access account.\n'
                'Check to make sure that the above credentials are valid.')
        }, http_status.HTTP_400_BAD_REQUEST

    organization_info = utils.get_organization_info(microsoftteams_tenant, access_token)
    if not organization_info:
        return {
            'message': ('Unable to access account.\n'
                'Check to make sure that the above credentials are valid.')
        }, http_status.HTTP_400_BAD_REQUEST

    account = None

    displayName = organization_info['displayName']
    microsoft_tenant_id = organization_info['id']

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name=displayName,
            oauth_key='{}\t{}'.format(microsoftteams_client_id, microsoftteams_client_secret),
            oauth_secret=access_token,
            provider_id=microsoft_tenant_id,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='microsoftteams', provider_id=microsoft_tenant_id
        )
        if account.oauth_key != microsoftteams_client_id or account.oauth_secret != microsoftteams_client_secret:
            account.oauth_key = microsoftteams_client_id
            account.oauth_secret = microsoftteams_client_secret
            account.save()

    assert account is not None

    if not auth.user.external_accounts.filter(id=account.id).exists():
        auth.user.external_accounts.add(account)

    # Ensure My microsoftteams is enabled.
    auth.user.get_or_add_addon('microsoftteams', auth=auth)
    auth.user.save()

    return {}

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_microsoftteams(**kwargs):
    return use_ember_app()

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    allMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allMicrosoftTeamsJson = serializers.serialize('json', allMicrosoftTeams, ensure_ascii=False)
    upcomingMicrosoftTeamsJson = serializers.serialize('json', upcomingMicrosoftTeams, ensure_ascii=False)
    previousMicrosoftTeamsJson = serializers.serialize('json', previousMicrosoftTeams, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'microsoftteams-config',
                     'attributes': {
                         'all_microsoft_teams': allMicrosoftTeamsJson,
                         'upcoming_microsoft_teams': upcomingMicrosoftTeamsJson,
                         'previous_microsoft_teams': previousMicrosoftTeamsJson,
                         'app_name_microsoft_teams': settings.MICROSOFT_TEAMS,
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    allMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allMicrosoftTeamsJson = serializers.serialize('json', allMicrosoftTeams, ensure_ascii=False)
    upcomingMicrosoftTeamsJson = serializers.serialize('json', upcomingMicrosoftTeams, ensure_ascii=False)
    previousMicrosoftTeamsJson = serializers.serialize('json', previousMicrosoftTeams, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'microsoftteams-config',
                     'attributes': {
                         'all_microsoft_teams': allMicrosoftTeamsJson,
                         'upcoming_microsoft_teams': upcomingMicrosoftTeamsJson,
                         'previous_microsoft_teams': previousMicrosoftTeamsJson,
                     }}}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_request_api(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    requestData = request.get_data()
    requestDataJsonLoads = json.loads(requestData)
    action = requestDataJsonLoads['actionType']
    updateMeetingId = requestDataJsonLoads['updateMeetingId']
    deleteMeetingId = requestDataJsonLoads['deleteMeetingId']
    requestBody = requestDataJsonLoads['body']

    account = ExternalAccount.objects.get(
        provider='microsoftteams', id=account_id
    )
    logger.info('requestDataJsonLoads::' +str(requestDataJsonLoads))
    logger.info('requestBody:views::' +str(requestBody))
    if action == 'create':
        createdMeetings = utils.api_create_microsoft_teams_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_microsoft_teams_meeting(addon, account, createdMeetings)

    if action == 'update':
        utils.api_update_microsoft_teams_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_microsoft_teams_meeting(updateMeetingId, requestBody)

    if action == 'delete':
        utils.api_delete_microsoft_teams_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_microsoft_teams_meeting(deleteMeetingId)
    return {}

@must_be_valid_project
@must_have_permission(READ)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_get_meetings(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    tz = pytz.timezone('utc')
    sToday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    sYesterday = sToday + timedelta(days=-1)
    sTomorrow = sToday + timedelta(days=1)

    recentMeetings = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__gte=sYesterday, start_datetime__lt=sTomorrow + timedelta(days=1)).order_by('start_datetime')
    recentMeetingsJson = serializers.serialize('json', recentMeetings, ensure_ascii=False)
    recentMeetingsDict = json.loads(recentMeetingsJson)

    return {
        'recentMeetings': recentMeetingsDict,
    }

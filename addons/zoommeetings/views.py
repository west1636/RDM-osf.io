# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.zoommeetings import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.zoommeetings.serializer import ZoomMeetingsSerializer
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
from website.oauth.views import oauth_callback
from api.base.utils import waterbutler_api_url_for
from addons.zoommeetings import settings
from addons.zoommeetings import models
from addons.zoommeetings import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from oauthlib.common import generate_token
from framework.sessions import session
from osf.models import AbstractNode, BaseFileNode, Guid, Comment
logger = logging.getLogger(__name__)

zoommeetings_account_list = generic_views.account_list(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_get_config = generic_views.get_config(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_import_auth = generic_views.import_auth(
    SHORT_NAME,
    ZoomMeetingsSerializer
)

zoommeetings_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def zoommeetings_oauth_connect(auth, **kwargs):

    provider = get_service(SHORT_NAME)
    logger.info(str(provider.client_id))
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url

def zoommeetings_add_your_app(**kwargs):

    state = generate_token()
    if session.data.get('oauth_states') is None:
        session.data['oauth_states'] = {}
    # save state token to the session for confirmation in the callback
    session.data['oauth_states'][SHORT_NAME] = {'state': state}

    return oauth_callback(SHORT_NAME)

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_zoommeetings(**kwargs):
    return use_ember_app()

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def zoommeetings_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    allZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allZoomMeetingsJson = serializers.serialize('json', allZoomMeetings, ensure_ascii=False)
    upcomingZoomMeetingsJson = serializers.serialize('json', upcomingZoomMeetings, ensure_ascii=False)
    previousZoomMeetingsJson = serializers.serialize('json', previousZoomMeetings, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'zoommeetings-config',
                     'attributes': {
                         'all_zoom_meetings': allZoomMeetingsJson,
                         'upcoming_zoom_meetings': upcomingZoomMeetingsJson,
                         'previous_zoom_meetings': previousZoomMeetingsJson,
                         'app_name_zoom_meetings': settings.ZOOM_MEETINGS,
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def zoommeetings_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    allZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousZoomMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allZoomMeetingsJson = serializers.serialize('json', allZoomMeetings, ensure_ascii=False)
    upcomingZoomMeetingsJson = serializers.serialize('json', upcomingZoomMeetings, ensure_ascii=False)
    previousZoomMeetingsJson = serializers.serialize('json', previousZoomMeetings, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'zoommeetings-config',
                     'attributes': {
                         'all_zoom_meetings': allZoomMeetingsJson,
                         'upcoming_zoom_meetings': upcomingZoomMeetingsJson,
                         'previous_zoom_meetings': previousZoomMeetingsJson,
                     }}}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def zoommeetings_request_api(**kwargs):

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
        provider='zoommeetings', id=account_id
    )
    logger.info('requestDataJsonLoads::' +str(requestDataJsonLoads))
    logger.info('requestBody:views::' +str(requestBody))
    if action == 'create':
        createdMeetings = utils.api_create_zoom_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_zoom_meeting(addon, account, createdMeetings)

    if action == 'update':
        utils.api_update_zoom_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_zoom_meeting(updateMeetingId, requestBody)

    if action == 'delete':
        utils.api_delete_zoom_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_zoom_meeting(deleteMeetingId)
    return {}

@must_be_valid_project
@must_have_permission(READ)
@must_have_addon(SHORT_NAME, 'node')
def zoommeetings_get_meetings(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    tz = pytz.timezone('utc')
    sToday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    sYesterday = sToday + timedelta(days=-1)
    sTomorrow = sToday + timedelta(days=1)

    recentMeetings = models.ZoomMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=sYesterday, start_datetime__lt=sTomorrow + timedelta(days=1)).order_by('start_datetime')
    recentMeetingsJson = serializers.serialize('json', recentMeetings, ensure_ascii=False)
    recentMeetingsDict = json.loads(recentMeetingsJson)

    return {
        'recentMeetings': recentMeetingsDict,
    }

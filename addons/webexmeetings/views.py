# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.webexmeetings import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.webexmeetings.serializer import WebexMeetingsSerializer
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
from addons.webexmeetings import settings
from addons.webexmeetings import models
from addons.webexmeetings import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from osf.models import AbstractNode, BaseFileNode, Guid, Comment
from admin.rdm_addons.utils import validate_rdm_addons_allowed
from addons.webexmeetings import SHORT_NAME
from flask import redirect
from website.oauth.utils import get_service
logger = logging.getLogger(__name__)

webexmeetings_account_list = generic_views.account_list(
    SHORT_NAME,
    WebexMeetingsSerializer
)

webexmeetings_get_config = generic_views.get_config(
    SHORT_NAME,
    WebexMeetingsSerializer
)

webexmeetings_import_auth = generic_views.import_auth(
    SHORT_NAME,
    WebexMeetingsSerializer
)

webexmeetings_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

# Overrides oauth_connect
@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def webexmeetings_oauth_connect(auth, **kwargs):

    webex_client_id = request.json.get('webexmeetings_client_id')
    webex_client_secret = request.json.get('webexmeetings_client_secret')

    provider = get_service(SHORT_NAME)

    authorization_url = provider.get_authorization_url(webex_client_id)

    return authorization_url

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_webexmeetings(**kwargs):
    return use_ember_app()

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    allWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allWebexMeetingsJson = serializers.serialize('json', allWebexMeetings, ensure_ascii=False)
    upcomingWebexMeetingsJson = serializers.serialize('json', upcomingWebexMeetings, ensure_ascii=False)
    previousWebexMeetingsJson = serializers.serialize('json', previousWebexMeetings, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'webexmeetings-config',
                     'attributes': {
                         'all_webex_meetings': allWebexMeetingsJson,
                         'upcoming_webex_meetings': upcomingWebexMeetingsJson,
                         'previous_webex_meetings': previousWebexMeetingsJson,
                         'app_name_webex_meetings': settings.WEBEX_MEETINGS,
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    allWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()

    allWebexMeetingsJson = serializers.serialize('json', allWebexMeetings, ensure_ascii=False)
    upcomingWebexMeetingsJson = serializers.serialize('json', upcomingWebexMeetings, ensure_ascii=False)
    previousWebexMeetingsJson = serializers.serialize('json', previousWebexMeetings, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'webexmeetings-config',
                     'attributes': {
                         'all_webex_meetings': allWebexMeetingsJson,
                         'upcoming_webex_meetings': upcomingWebexMeetingsJson,
                         'previous_webex_meetings': previousWebexMeetingsJson,
                     }}}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_request_api(**kwargs):

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
        provider='webexmeetings', id=account_id
    )
    logger.info('requestDataJsonLoads::' +str(requestDataJsonLoads))
    logger.info('requestBody:views::' +str(requestBody))

    return {}

@must_be_valid_project
@must_have_permission(READ)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_get_meetings(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    tz = pytz.timezone('utc')
    sToday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    sYesterday = sToday + timedelta(days=-1)
    sTomorrow = sToday + timedelta(days=1)

    recentMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=sYesterday, start_datetime__lt=sTomorrow + timedelta(days=1)).order_by('start_datetime')
    recentMeetingsJson = serializers.serialize('json', recentMeetings, ensure_ascii=False)
    recentMeetingsDict = json.loads(recentMeetingsJson)

    return {
        'recentMeetings': recentMeetingsDict,
    }

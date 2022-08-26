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
from addons.base.exceptions import InvalidAuthError
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

    provider = get_service(SHORT_NAME)
    logger.info(str(provider.client_id))
    authorization_url = provider.get_authorization_url(provider.client_id)

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
    auth = kwargs['auth']
    user = auth.user

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    allWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(email_address__exact='').exclude(email_address__isnull=True)
    nodeWebexMeetingsAttendeesRelation = models.WebexMeetingsAttendeesRelation.objects.filter(webex_meetings__node_settings_id=addon.id)

    allWebexMeetingsJson = serializers.serialize('json', allWebexMeetings, ensure_ascii=False)
    upcomingWebexMeetingsJson = serializers.serialize('json', upcomingWebexMeetings, ensure_ascii=False)
    previousWebexMeetingsJson = serializers.serialize('json', previousWebexMeetings, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebexMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = utils.makeInstitutionUserList(users)

    try:
        access_token = addon.fetch_access_token()
    except InvalidAuthError:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    return {'data': {'id': node._id, 'type': 'webexmeetings-config',
                     'attributes': {
                         'all_webex_meetings': allWebexMeetingsJson,
                         'upcoming_webex_meetings': upcomingWebexMeetingsJson,
                         'previous_webex_meetings': previousWebexMeetingsJson,
                         'app_name_webex_meetings': settings.WEBEX_MEETINGS,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_webex_meetings_attendees_relation': nodeWebexMeetingsAttendeesRelationJson,
                         'institution_users': institutionUsers
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    auth = kwargs['auth']
    user = auth.user

    allWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebexMeetings = models.WebexMeetings.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeAttendeesAll = models.Attendees.objects.filter(node_settings_id=addon.id)
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(email_address__exact='').exclude(email_address__isnull=True)
    nodeWebexMeetingsAttendeesRelation = models.WebexMeetingsAttendeesRelation.objects.filter(webex_meetings__node_settings_id=addon.id)

    allWebexMeetingsJson = serializers.serialize('json', allWebexMeetings, ensure_ascii=False)
    upcomingWebexMeetingsJson = serializers.serialize('json', upcomingWebexMeetings, ensure_ascii=False)
    previousWebexMeetingsJson = serializers.serialize('json', previousWebexMeetings, ensure_ascii=False)
    nodeAttendeesAllJson = serializers.serialize('json', nodeAttendeesAll, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebexMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = utils.makeInstitutionUserList(users)

    return {'data': {'id': node._id, 'type': 'webexmeetings-config',
                     'attributes': {
                         'all_webex_meetings': allWebexMeetingsJson,
                         'upcoming_webex_meetings': upcomingWebexMeetingsJson,
                         'previous_webex_meetings': previousWebexMeetingsJson,
                         'node_attendees_all': nodeAttendeesAllJson,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_webex_meetings_attendees_relation': nodeWebexMeetingsAttendeesRelationJson,
                         'institution_users': institutionUsers
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

    if action == 'create':
        createdMeetings = utils.api_create_webex_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_webex_meeting(addon, account, createdMeetings)

    if action == 'update':
        updatedMeetings = utils.api_update_webex_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_webex_meeting(updateMeetingId, requestDataJsonLoads, updatedMeetings, addon, account)

    if action == 'delete':
        utils.api_delete_webex_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_webex_meeting(deleteMeetingId)

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_register_email(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider='webexmeetings', id=account_id
    )
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info('Register or Update Web Meeting Email: ' + str(requestDataJson))
    _id = requestDataJson.get('_id', '')
    guid = requestDataJson.get('guid', '')
    fullname = requestDataJson.get('fullname', '')
    email = requestDataJson.get('email', '')
    is_guest = requestDataJson.get('is_guest', True)
    actionType = requestDataJson.get('actionType', '')
    displayName = ''

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)

    if actionType == 'create':
        if not is_guest:
            fullname = OSFUser.objects.get(guids___id=guid).fullname
            displayName = api_get_webex_meetings_username(account, email)

        attendee = models.Attendees(
            user_guid=guid,
            fullname=fullname,
            is_guest=is_guest,
            email_address=email,
            display_name=displayName,
            node_settings=nodeSettings,
        )
        attendee.save()
    elif actionType == 'update':
        if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, _id=_id).exists():
            attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
            if not is_guest:
                attendee.fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname
                attendee.displayName = api_get_webex_meetings_username(account, email)
            attendee.email_address = email
            attendee.save()
    elif actionType == 'delete':
        attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
        attendee.delete()
    else:
        if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, _id=_id).exists():
            attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
            if not is_guest:
                attendee.fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname
            attendee.email_address = email
            attendee.save()
        else:
            if not is_guest:
                fullname = OSFUser.objects.get(guids___id=guid).fullname

            attendeeInfo = models.Attendees(
                user_guid=guid,
                fullname=fullname,
                is_guest=is_guest,
                email_address=email,
                node_settings=nodeSettings,
            )
            attendeeInfo.save()

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

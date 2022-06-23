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
from addons.microsoftteams import settings
from addons.microsoftteams import models
from addons.microsoftteams import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from website.oauth.utils import get_service
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
def microsoftteams_oauth_connect(auth, **kwargs):

    provider = get_service(SHORT_NAME)
    logger.info(str(provider.client_id))
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url
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
    auth = kwargs['auth']
    user = auth.user

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    allMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)

    allMicrosoftTeamsJson = serializers.serialize('json', allMicrosoftTeams, ensure_ascii=False)
    upcomingMicrosoftTeamsJson = serializers.serialize('json', upcomingMicrosoftTeams, ensure_ascii=False)
    previousMicrosoftTeamsJson = serializers.serialize('json', previousMicrosoftTeams, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = utils.makeInstitutionUserList(users)

    try:
        access_token = addon.fetch_access_token()
    except InvalidAuthError:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    return {'data': {'id': node._id, 'type': 'microsoftteams-config',
                     'attributes': {
                         'all_microsoft_teams': allMicrosoftTeamsJson,
                         'upcoming_microsoft_teams': upcomingMicrosoftTeamsJson,
                         'previous_microsoft_teams': previousMicrosoftTeamsJson,
                         'app_name_microsoft_teams': settings.MICROSOFT_TEAMS,
                         'node_microsoft_teams_attendees': nodeMicrosoftTeamsAttendeesJson,
                         'institution_users': institutionUsers
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    allMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousMicrosoftTeams = models.MicrosoftTeams.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)

    allMicrosoftTeamsJson = serializers.serialize('json', allMicrosoftTeams, ensure_ascii=False)
    upcomingMicrosoftTeamsJson = serializers.serialize('json', upcomingMicrosoftTeams, ensure_ascii=False)
    previousMicrosoftTeamsJson = serializers.serialize('json', previousMicrosoftTeams, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = utils.makeInstitutionUserList(users)

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
        createdMeetings = utils.api_create_teams_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_teams_meeting(addon, account, createdMeetings)

    if action == 'update':
        updatedMeetings = utils.api_update_teams_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_teams_meeting(updateMeetingId, updatedMeetings)

    if action == 'delete':
        utils.api_delete_teams_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_teams_meeting(deleteMeetingId)

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_register_teams_email(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider='microsoftteams', id=account_id
    )
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info('Register or Update Web Meeting Email: ' + str(requestDataJson))
    _id = requestDataJson['_id']
    guid = requestDataJson['guid']
    fullname = requestDataJson['fullname']
    email = requestDataJson['email']
    is_guest = requestDataJson['is_guest']

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    nodeId = nodeSettings.id

    if models.Attendees.objects.filter(node_settings_id=nodeId, _id=_id).exists():
        attendee = models.Attendees.objects.get(node_settings_id=nodeId, _id=_id)
        if not is_guest:
            attendee.fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname
        attendee.microsoft_teams_mail = email
        attendee.save()
    else:
        if not is_guest:
            fullname = OSFUser.objects.get(guids___id=guid).fullname
            username = utils.getMicrosoftUserName(account, email)

        attendeeInfo = models.Attendees(
            user_guid=guid,
            fullname=fullname,
            is_guest=is_guest,
            microsoft_teams_mail=email,
            microsoft_teams_user_name=username,
            node_settings=nodeSettings,
        )
        attendeeInfo.save()

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

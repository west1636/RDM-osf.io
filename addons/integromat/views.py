# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json

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
from addons.integromat import settings

from addons.integromat import models
from osf.models.rdm_integromat import RdmWebMeetingApps, RdmWorkflows
from django.core import serializers

import execjs
import PyV8

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

    try:
        access_token = request.json.get('integromat_api_token')
        webhook_url = request.json.get('integromat_webhook_url')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    integromatUserInfo = authIntegromat(access_token, settings.H_SDK_VERSION)

    if not integromatUserInfo:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)
    else:
        integromat_userid = integromatUserInfo['id']
        integromat_username = integromatUserInfo['name']

    user = auth.user

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name=integromat_username,
            oauth_key=access_token,
            provider_id=integromat_userid,
            webhook_url=webhook_url,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id=integromat_userid
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

    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request('GET', settings.INTEGROMAT_API_WHOAMI, headers=headers, data=payload)
    userInfo = response.json()

    if not userInfo.viewkeys() >= {'id', 'name', 'email', 'scope'}:

        message = ''

        if userInfo.viewkeys() >= {'message'}:
            message = userInfo['message']

        logger.info('Integromat Authentication failure:' + message)

        userInfo.clear()

    return userInfo

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_integromat(**kwargs):
    return use_ember_app()

@must_be_valid_project
#@must_have_permission('admin')
@must_be_logged_in
@must_have_addon(SHORT_NAME, 'node')
def integromat_get_config_ember(auth, **kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    user = auth.user

    qsUserGuid = user._prefetched_objects_cache['guids'].only()
    userGuidSerializer = serializers.serialize('json', qsUserGuid, ensure_ascii=False)
    userGuidJson = json.loads(userGuidSerializer)
    userGuid = userGuidJson[0]['fields']['_id']
    organizer = models.Attendees.objects.get(user_guid=userGuid)
    organizerId = organizer.microsoft_teams_user_object

    appMicrosoftTeams = RdmWebMeetingApps.objects.get(app_name='MicrosoftTeams')

    workflows = RdmWorkflows.objects.all()
    microsoftTeamsMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, app_id=appMicrosoftTeams.id)
    microsoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id)

    microsoftTeamsAttendeesJson = serializers.serialize('json', microsoftTeamsAttendees, ensure_ascii=False)
    workflowsJson = serializers.serialize('json', workflows, ensure_ascii=False)
    microsoftTeamsMeetingsJson = serializers.serialize('json', microsoftTeamsMeetings, ensure_ascii=False)

    return {'data': {'id': node._id, 'type': 'integromat-config',
                     'attributes': {
                         'node_settings_id': addon._id, 
                         'webhook_url': addon.external_account.webhook_url,
                         'microsoft_teams_meetings': microsoftTeamsMeetingsJson,
                         'microsoft_teams_attendees': microsoftTeamsAttendeesJson,
                         'workflows': workflowsJson,
                         'app_name_microsoft_teams' : settings.MICROSOFT_TEAMS,
                         'info_grdm_scenario_processing': settings.INFO_GRDM_SCENARIO_PROCESSING,
                         'organizer_id': organizerId
                     }}}

#api for Integromat action
def integromat_api_call(**kwargs):

    logger.info('integromat called integromat_api_call.GRDM-Integromat connection test scceeeded.')

    return {}

def integromat_create_meeting_info(**kwargs):

    nodeId = request.get_json().get('nodeId')
    appName = request.get_json().get('meetingAppName')
    subject = request.get_json().get('subject')
    organizer = request.get_json().get('organizer')
    attendees = request.get_json().get('attendees')
    startDatetime = request.get_json().get('startDate')
    endDatetime = request.get_json().get('endDate')
    location = request.get_json().get('location')
    content = request.get_json().get('content')
    joinUrl = request.get_json().get('microsoftTeamsJoinUrl')
    meetingId = request.get_json().get('microsoftTeamsMeetingId')

    try:
        node = models.NodeSettings.objects.get(_id=nodeId)
    except:
        logger.error('nodesettings _id is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    try:
        webApp = RdmWebMeetingApps.objects.get(app_name=appName)
    except:
        logger.error('web app name is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)


    meetingInfo = models.AllMeetingInformation(
        subject = subject,
        organizer = organizer,
        start_datetime = startDatetime,
        end_datetime = endDatetime,
        location = location,
        content = content,
        join_url = joinUrl,
        meetingid = meetingId,
        app_id = webApp.id,
        node_settings_id = node.id,
        )
    meetingInfo.save()

    attendeeIds = []

    for attendeeMail in attendees:

        qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, microsoft_teams_mail=attendeeMail)
        attendeeId = qsAttendee.id
        attendeeIds.append(attendeeId)

    meetingInfo.attendees = attendeeIds
    meetingInfo.save()

    return {}

def integromat_update_meeting_info(**kwargs):

    nodeId = request.get_json().get('nodeId')
    appName = request.get_json().get('meetingAppName')
    subject = request.get_json().get('subject')
    attendees = request.get_json().get('attendees')
    startDatetime = request.get_json().get('startDate')
    endDatetime = request.get_json().get('endDate')
    location = request.get_json().get('location')
    content = request.get_json().get('content')
    meetingId = request.get_json().get('microsoftTeamsMeetingId')
    logger.info('meetingId::' + str(meetingId))
    qsUpdateMeetingInfo = models.AllMeetingInformation.objects.get(meetingid=meetingId)

    qsUpdateMeetingInfo.subject = subject
    qsUpdateMeetingInfo.start_datetime = startDatetime
    qsUpdateMeetingInfo.end_datetime = endDatetime
    qsUpdateMeetingInfo.location = location
    qsUpdateMeetingInfo.content = content

    try:
        node = models.NodeSettings.objects.get(_id=nodeId)
    except:
        logger.error('nodesettings _id is invalid.')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    attendeeIds = []

    for attendeeMail in attendees:

        qsAttendee = models.Attendees.objects.get(node_settings_id=node.id, microsoft_teams_mail=attendeeMail)
        attendeeId = qsAttendee.id
        attendeeIds.append(attendeeId)


    qsUpdateMeetingInfo.attendees = attendeeIds

    qsUpdateMeetingInfo.save()

    return {}

def integromat_delete_meeting_info(**kwargs):

    nodeId = request.get_json().get('nodeId')
    appName = request.get_json().get('meetingAppName')
    meetingIds = request.get_json().get('microsoftTeamsMeetingIds')
    logger.info('meetingIds:' + str(meetingIds))
    for meetingId in meetingIds:
         qsDeleteMeeting = models.AllMeetingInformation.objects.get(meetingid=meetingId)
         qsDeleteMeeting.delete()

    return {}


@must_be_valid_project
#@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def integromat_add_microsoft_teams_user(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    userGuid = request.get_json().get('user_guid')
    microsoftTeamsUserObject = request.get_json().get('microsoft_teams_user_object')
    microsoftTeamsMail = request.get_json().get('microsoft_teams_mail')

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    nodeNum = nodeSettings.id
    if models.Attendees.objects.filter(node_settings_id=nodeNum, user_guid=userGuid).exists():
        logger.info('user_guid deplicated')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    if models.Attendees.objects.filter(node_settings_id=nodeNum, microsoft_teams_user_object=microsoftTeamsUserObject).exists():
        logger.info('Microsoft User Object ID deplicated')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    if models.Attendees.objects.filter(node_settings_id=nodeNum, microsoft_teams_mail=microsoftTeamsMail).exists():
        logger.info('Microsoft Teams Sign-in Address')
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    microsoftTeamsUserInfo = models.Attendees(
        user_guid = userGuid,
        microsoft_teams_user_object = microsoftTeamsUserObject,
        microsoft_teams_mail = microsoftTeamsMail,
        node_settings = nodeSettings,

        )

    microsoftTeamsUserInfo.save()

    return {}

@must_be_valid_project
#@must_have_permission('admin')
@must_have_addon(SHORT_NAME, 'node')
def integromat_delete_microsoft_teams_user(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    userGuid = request.get_json().get('user_guid')

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    nodeNum = nodeSettings.id
    qsMicrosoftTeamsUserInfo =  models.Attendees.objects.filter(node_settings_id=nodeNum, user_guid=userGuid)

    qsMicrosoftTeamsUserInfo.delete()

    return {}

def integromat_info_msg(**kwargs):

    msgKey = request.get_json().get('notifyType')
    infoMsg = ''

    if msgKey == settings.INFO_GRDM_SCENARIO_PROCESSING:
        infoMsg = 'The workflow is running.'

    logger.info('msgKey:' + msgKey)

    return {}

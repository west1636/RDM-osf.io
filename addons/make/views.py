# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.make import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.make.serializer import MakeSerializer
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
from addons.make import settings
from addons.make import models
from addons.make import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from osf.models import AbstractNode, BaseFileNode, Guid, Comment
logger = logging.getLogger(__name__)

make_account_list = generic_views.account_list(
    SHORT_NAME,
    MakeSerializer
)

make_get_config = generic_views.get_config(
    SHORT_NAME,
    MakeSerializer
)

make_import_auth = generic_views.import_auth(
    SHORT_NAME,
    MakeSerializer
)

make_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def make_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    try:
        access_token = request.json.get('integromat_api_token')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    integromatUserInfo = authIntegromat(access_token, settings.H_SDK_VERSION)

    if not integromatUserInfo:
        return {
            'message': ('Unable to access account.\n'
                'Check to make sure that the above credentials are valid, ')
        }, http_status.HTTP_400_BAD_REQUEST
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

    if not user.external_accounts.filter(id=account.id).exists():

        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    return {}

def authIntegromat(access_token, hSdkVersion):

    message = ''
    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request('GET', settings.INTEGROMAT_API_WHOAMI, headers=headers, data=payload)
    status_code = response.status_code
    userInfo = response.json()

    if status_code != 200:

        if userInfo.keys() >= {'message'}:
            message = userInfo['message']

        logger.info('Failed to authenticate Integromat account' + '[' + str(status_code) + ']' + ':' + message)

        userInfo.clear()

    return userInfo

# ember: ここから
@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def project_grdmapps(**kwargs):
    return use_ember_app()

def makeInstitutionUserList(users):

    institutionUsers = []
    userInfo = {}
    for user in users:
        userInfo = {}
        userInfo['guid'] = user._id
        userInfo['fullname'] = user.fullname
        userInfo['username'] = user.username
        institutionUsers.append(userInfo)

    ret = json.dumps(institutionUsers)

    return ret

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def grdmapps_get_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    auth = kwargs['auth']
    user = auth.user

    if not addon.complete:
        raise HTTPError(http_status.HTTP_403_FORBIDDEN)

    workflowsJson = json.dumps(settings.RDM_WORKFLOW)
    allWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    webMeetingAppsJson = json.dumps(settings.RDM_WEB_MEETING_APPS)
    nodeAttendeesAll = models.Attendees.objects.filter(node_settings_id=addon.id)
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(webex_meetings_mail__exact='').exclude(webex_meetings_mail__isnull=True)
    nodeZoomMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(zoom_meetings_mail__exact='').exclude(zoom_meetings_mail__isnull=True)
    nodeWorkflows = models.NodeWorkflows.objects.filter(node_settings_id=addon.id)
    nodeWebMeetingsAttendeesRelation = models.AllMeetingInformationAttendeesRelation.objects.filter(all_meeting_information__node_settings_id=addon.id)

    allWebMeetingsJson = serializers.serialize('json', allWebMeetings, ensure_ascii=False)
    upcomingWebMeetingsJson = serializers.serialize('json', upcomingWebMeetings, ensure_ascii=False)
    previousWebMeetingsJson = serializers.serialize('json', previousWebMeetings, ensure_ascii=False)
    nodeAttendeesAllJson = serializers.serialize('json', nodeAttendeesAll, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeZoomMeetingsAttendeesJson = serializers.serialize('json', nodeZoomMeetingsAttendees, ensure_ascii=False)
    nodeWorkflowsJson = serializers.serialize('json', nodeWorkflows, ensure_ascii=False)
    nodeWebMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)

    institutionUsers = makeInstitutionUserList(users)

    return {'data': {'id': node._id, 'type': 'grdmapps-config',
                     'attributes': {
                         'node_settings_id': addon._id,
                         'all_web_meetings': allWebMeetingsJson,
                         'upcoming_web_meetings': upcomingWebMeetingsJson,
                         'previous_web_meetings': previousWebMeetingsJson,
                         'node_attendees_all': nodeAttendeesAllJson,
                         'node_microsoft_teams_attendees': nodeMicrosoftTeamsAttendeesJson,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_web_meetings_attendees_relation': nodeWebMeetingsAttendeesRelationJson,
                         'node_zoom_meetings_attendees': nodeZoomMeetingsAttendeesJson,
                         'workflows': workflowsJson,
                         'node_workflows': nodeWorkflowsJson,
                         'web_meeting_apps': webMeetingAppsJson,
                         'app_name_microsoft_teams': settings.MICROSOFT_TEAMS,
                         'app_name_webex_meetings': settings.WEBEX_MEETINGS,
                         'app_name_zoom_meetings': settings.ZOOM_MEETINGS,
                         'institution_users': institutionUsers
                     }}}

@must_be_valid_project
@must_have_addon(SHORT_NAME, 'node')
def grdmapps_set_config_ember(**kwargs):
    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    auth = kwargs['auth']
    user = auth.user

    allWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id).order_by('start_datetime').reverse()
    upcomingWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=datetime.today()).order_by('start_datetime')
    previousWebMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__lt=datetime.today()).order_by('start_datetime').reverse()
    nodeAttendeesAll = models.Attendees.objects.filter(node_settings_id=addon.id)
    nodeMicrosoftTeamsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(microsoft_teams_mail__exact='').exclude(microsoft_teams_mail__isnull=True)
    nodeWebexMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(webex_meetings_mail__exact='').exclude(webex_meetings_mail__isnull=True)
    nodeZoomMeetingsAttendees = models.Attendees.objects.filter(node_settings_id=addon.id).exclude(zoom_meetings_mail__exact='').exclude(zoom_meetings_mail__isnull=True)
    nodeWorkflows = models.NodeWorkflows.objects.filter(node_settings_id=addon.id)
    nodeWebMeetingsAttendeesRelation = models.AllMeetingInformationAttendeesRelation.objects.filter(all_meeting_information__node_settings_id=addon.id)

    allWebMeetingsJson = serializers.serialize('json', allWebMeetings, ensure_ascii=False)
    upcomingWebMeetingsJson = serializers.serialize('json', upcomingWebMeetings, ensure_ascii=False)
    previousWebMeetingsJson = serializers.serialize('json', previousWebMeetings, ensure_ascii=False)
    nodeAttendeesAllJson = serializers.serialize('json', nodeAttendeesAll, ensure_ascii=False)
    nodeMicrosoftTeamsAttendeesJson = serializers.serialize('json', nodeMicrosoftTeamsAttendees, ensure_ascii=False)
    nodeWebexMeetingsAttendeesJson = serializers.serialize('json', nodeWebexMeetingsAttendees, ensure_ascii=False)
    nodeZoomMeetingsAttendeesJson = serializers.serialize('json', nodeZoomMeetingsAttendees, ensure_ascii=False)
    nodeWorkflowsJson = serializers.serialize('json', nodeWorkflows, ensure_ascii=False)
    nodeWebMeetingsAttendeesRelationJson = serializers.serialize('json', nodeWebMeetingsAttendeesRelation, ensure_ascii=False)

    institutionId = rdm_utils.get_institution_id(user)
    users = OSFUser.objects.filter(affiliated_institutions__id=institutionId)
    institutionUsers = makeInstitutionUserList(users)

    return {'data': {'id': node._id, 'type': 'grdmapps-config',
                     'attributes': {
                         'all_web_meetings': allWebMeetingsJson,
                         'upcoming_web_meetings': upcomingWebMeetingsJson,
                         'previous_web_meetings': previousWebMeetingsJson,
                         'node_attendees_all': nodeAttendeesAllJson,
                         'node_microsoft_teams_attendees': nodeMicrosoftTeamsAttendeesJson,
                         'node_webex_meetings_attendees': nodeWebexMeetingsAttendeesJson,
                         'node_web_meetings_attendees_relation': nodeWebMeetingsAttendeesRelationJson,
                         'node_zoom_meetings_attendees': nodeZoomMeetingsAttendeesJson,
                         'node_workflows': nodeWorkflowsJson,
                         'institution_users': institutionUsers
                     }}}

#api for Integromat action
def make_api_call(*args, **kwargs):

    auth = Auth.from_kwargs(request.args.to_dict(), kwargs)
    user = auth.user

    # User must be logged in
    if user is None:
        raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)

    logger.info('Integromat called integromat_api_call by ' + str(user) + '.')
    logger.info('GRDM-Integromat connection test scceeeded.')

    return {'email': str(user)}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_get_file_id(auth, **kwargs):

    node = kwargs['node'] or kwargs['project']

    title = request.get_json().get('title')
    file_path = ''
    guid = utils.get_guid(node)
    auth_headers = request.headers.environ['HTTP_AUTHORIZATION']

    response = requests.get(
        waterbutler_api_url_for(
            guid, 'osfstorage', path='/', _internal=True, meta=''
        ),
        headers={
            'content-type': 'application/json',
            'authorization': auth_headers,
        }
    )

    filesInfo = response.json()['data']

    for fileInfo in filesInfo:
        if title == fileInfo['attributes']['name']:
            file_path = fileInfo['attributes']['path']

    return {'filePath': file_path}

def make_get_node(*args, **kwargs):
    auth = Auth.from_kwargs(request.args.to_dict(), kwargs)
    user = auth.user
    logger.info('auth:' + str(user))
    if not user:
        raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)

    guid = request.get_json().get('guid')
    slackChannelId = request.get_json().get('slackChannelId')
    root_guid = None
    nodeType = None
    reqBody = {}

    if guid and not slackChannelId:

        try:
            targetNode = AbstractNode.objects.get(guids___id=guid)
            # User must have permissions
            if not targetNode.has_permission(user, READ):
                raise HTTPError(http_status.HTTP_403_FORBIDDEN)
            nodeType = AbstractNode.objects.get(guids___id=guid).target_type
            title = AbstractNode.objects.get(guids___id=guid).title
            try:
                slack_channel_id = models.NodeFileWebappMap.objects.get(node_file_guid=guid).slack_channel_id
            except ObjectDoesNotExist:
                slack_channel_id = ''
        except ObjectDoesNotExist:
            try:
                nodeType = BaseFileNode.objects.get(guids___id=guid).target_type
            except ObjectDoesNotExist:
                raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(message_short='GUID does not exixt.'))
            title = BaseFileNode.objects.get(guids___id=guid).name
            targetObjectId = BaseFileNode.objects.get(guids___id=guid).target_object_id
            targetNode = AbstractNode.objects.get(id=targetObjectId)
            # User must have permissions
            if not targetNode.has_permission(user, READ):
                raise HTTPError(http_status.HTTP_403_FORBIDDEN)
            root_guid = utils.get_guid(targetNode)
            try:
                slack_channel_id = models.NodeFileWebappMap.objects.get(node_file_guid=guid).slack_channel_id
            except ObjectDoesNotExist:
                slack_channel_id = ''

        reqBody = {
            'title': title,
            'slackChannelId': slack_channel_id,
            'guid': guid,
            'rootGuid': root_guid
        }

    if slackChannelId and not guid:

        try:
            guid = models.NodeFileWebappMap.objects.get(slack_channel_id=slackChannelId).node_file_guid
        except ObjectDoesNotExist:
            raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(message_short='Slack Channel ID does not registered.'))

        try:
            targetNode = AbstractNode.objects.get(guids___id=guid)
            # User must have permissions
            if not targetNode.has_permission(user, READ):
                raise HTTPError(http_status.HTTP_403_FORBIDDEN)
            nodeType = AbstractNode.objects.get(guids___id=guid).target_type
        except ObjectDoesNotExist:
            nodeType = BaseFileNode.objects.get(guids___id=guid).target_type
            targetObjectId = BaseFileNode.objects.get(guids___id=guid).target_object_id
            targetNode = AbstractNode.objects.get(id=targetObjectId)
            # User must have permissions
            if not targetNode.has_permission(user, READ):
                raise HTTPError(http_status.HTTP_403_FORBIDDEN)
            root_guid = utils.get_guid(targetNode)

        reqBody = {
            'guid': guid,
            'rootGuid': root_guid
        }

    reqBody['nodeType'] = nodeType

    return reqBody

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def make_link_to_node(**kwargs):

    guid = request.get_json().get('guid')
    slack_channel_id = request.get_json().get('slackChannelId')
    qsNodeFileWebappMap = models.NodeFileWebappMap(slack_channel_id=slack_channel_id, node_file_guid=guid)
    try:
        qsNodeFileWebappMap.save()
    except ValidationError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(message_short='Check your GUID or Slack Channel ID.'))

    return {}

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def make_watch_comment(**kwargs):

    guid = request.get_json().get('guid')
    try:
        rootTargetId = Guid.objects.get(_id=guid)
    except ObjectDoesNotExist:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(message_short='GUID does not exixt.'))

    updatedComments = Comment.objects.filter(root_target_id=rootTargetId)
    updatedCommentsJson = serializers.serialize('json', updatedComments, ensure_ascii=False)
    updatedCommentsDict = json.loads(updatedCommentsJson)
    qsSlackChannelId = models.NodeFileWebappMap.objects.filter(node_file_guid=guid)
    qsSlackChannelIdJson = serializers.serialize('json', qsSlackChannelId, ensure_ascii=False)
    qsSlackChannelIdDict = json.loads(qsSlackChannelIdJson)
    slack_channel_id = qsSlackChannelIdDict[0]['fields']['slack_channel_id'] if len(qsSlackChannelId) == 1 else None
    retComments = {'guid': guid, 'slackChannelId': slack_channel_id, 'data': []}

    for comment in updatedCommentsDict:
        commentsInfo = {}
        commentsInfo['id'] = comment['pk']
        commentsInfo['content'] = comment['fields']['content']
        commentsInfo['modified'] = comment['fields']['modified']
        commentsInfo['user'] = OSFUser.objects.get(id=comment['fields']['user']).fullname
        retComments['data'].append(commentsInfo)

    return retComments

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_register_web_meeting_apps_email(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info('Register or Update Web Meeting Email: ' + str(requestDataJson))
    _id = requestDataJson['_id']
    guid = requestDataJson['guid']
    fullname = requestDataJson['fullname']
    appName = requestDataJson['appName']
    email = requestDataJson['email']
    username = requestDataJson['username']
    is_guest = requestDataJson['is_guest']

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    nodeId = nodeSettings.id

    if models.Attendees.objects.filter(node_settings_id=nodeId, _id=_id).exists():

        webMeetingAppAttendee = models.Attendees.objects.get(node_settings_id=nodeId, _id=_id)

        if not is_guest:
            webMeetingAppAttendee.fullname = OSFUser.objects.get(guids___id=webMeetingAppAttendee.user_guid).fullname

        if appName == settings.MICROSOFT_TEAMS:

            webMeetingAppAttendee.microsoft_teams_mail = email
            if username:
                webMeetingAppAttendee.microsoft_teams_user_name = username
        elif appName == settings.WEBEX_MEETINGS:

            webMeetingAppAttendee.webex_meetings_mail = email
            if username:
                webMeetingAppAttendee.webex_meetings_display_name = username

        elif appName == settings.ZOOM_MEETINGS:

            webMeetingAppAttendee.zoom_meetings_mail = email

        webMeetingAppAttendee.save()
    else:

        if not is_guest:
            fullname = OSFUser.objects.get(guids___id=guid).fullname

            if appName == settings.MICROSOFT_TEAMS:

                if models.Attendees.objects.filter(node_settings_id=nodeId, user_guid=guid).exists():

                    webMeetingAppAttendeeInfo = models.Attendees.objects.get(node_settings_id=nodeId, user_guid=guid)
                    webMeetingAppAttendeeInfo.fullname = fullname
                    webMeetingAppAttendeeInfo.microsoft_teams_user_name = username
                    webMeetingAppAttendeeInfo.microsoft_teams_mail = email

                else:

                    webMeetingAppAttendeeInfo = models.Attendees(
                        user_guid=guid,
                        fullname=fullname,
                        is_guest=is_guest,
                        microsoft_teams_user_name=username,
                        microsoft_teams_mail=email,
                        node_settings=nodeSettings,
                    )

            elif appName == settings.WEBEX_MEETINGS:

                if models.Attendees.objects.filter(node_settings_id=nodeId, user_guid=guid).exists():

                    webMeetingAppAttendeeInfo = models.Attendees.objects.get(node_settings_id=nodeId, user_guid=guid)
                    webMeetingAppAttendeeInfo.fullname = fullname
                    webMeetingAppAttendeeInfo.webex_meetings_display_name = username
                    webMeetingAppAttendeeInfo.webex_meetings_mail = email

                else:

                    webMeetingAppAttendeeInfo = models.Attendees(
                        user_guid=guid,
                        fullname=fullname,
                        is_guest=is_guest,
                        webex_meetings_display_name=username,
                        webex_meetings_mail=email,
                        node_settings=nodeSettings,
                    )

            elif appName == settings.ZOOM_MEETINGS:
                pass

        else:

            if appName == settings.MICROSOFT_TEAMS:

                webMeetingAppAttendeeInfo = models.Attendees(
                    user_guid=guid,
                    fullname=fullname,
                    is_guest=is_guest,
                    microsoft_teams_user_name=username,
                    microsoft_teams_mail=email,
                    node_settings=nodeSettings,
                )
            elif appName == settings.WEBEX_MEETINGS:

                webMeetingAppAttendeeInfo = models.Attendees(
                    user_guid=guid,
                    fullname=fullname,
                    is_guest=is_guest,
                    webex_meetings_display_name=username,
                    webex_meetings_mail=email,
                    node_settings=nodeSettings,
                )
            elif appName == settings.ZOOM_MEETINGS:

                webMeetingAppAttendeeInfo = models.Attendees(
                    user_guid=guid,
                    fullname=fullname,
                    is_guest=is_guest,
                    zoom_meetings_mail=email,
                    node_settings=nodeSettings,
                )

        webMeetingAppAttendeeInfo.save()

    return {}

def register_instituion_users_zoom_attendees(nodeSettings, attendees):

    for email in attendees:
        if not models.Attendees.objects.filter(node_settings_id=nodeSettings.id, zoom_meetings_mail=email).exists():
            user = OSFUser.objects.get(username=email)
            qsUserGuid = user._prefetched_objects_cache['guids'].only()
            userGuidSerializer = serializers.serialize('json', qsUserGuid, ensure_ascii=False)
            userGuidJson = json.loads(userGuidSerializer)
            userGuid = userGuidJson[0]['fields']['_id']
            try:
                attendeeObjUpdate = models.Attendees.objects.get(node_settings_id=nodeSettings.id, user_guid=userGuid)
                attendeeObjUpdate.zoom_meetings_mail = email
                attendeeObjUpdate.save()
            except ObjectDoesNotExist:
                fullname = user.fullname
                attendeeObjCreate = models.Attendees(
                    user_guid=userGuid,
                    fullname=fullname,
                    is_guest=False,
                    zoom_meetings_mail=email,
                    node_settings=nodeSettings,
                )
                attendeeObjCreate.save()

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_start_scenario(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    requestData = request.get_data()
    requestDataJsonLoads = json.loads(requestData)
    timestamp = requestDataJsonLoads['timestamp']
    appName = requestDataJsonLoads['appName']
    attendees = requestDataJsonLoads['attendees']
    webhook_url = requestDataJsonLoads['webhookUrl']

    if appName == settings.ZOOM_MEETINGS:
        register_instituion_users_zoom_attendees(addon, attendees)

    requestDataJsonLoads.pop('webhookUrl')
    requestDataJson = json.dumps(requestDataJsonLoads)

    response = requests.post(webhook_url, data=requestDataJson, headers={'Content-Type': 'application/json'})
    response.raise_for_status()

    return {
        'timestamp': timestamp
    }

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_req_next_msg(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    time.sleep(1)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    timestamp = requestDataJson['timestamp']
    nodeId = addon._id

    notify = False
    count = requestDataJson['count']

    integromatMsg = ''
    node = models.NodeSettings.objects.get(_id=nodeId)

    if count == settings.TIME_LIMIT_START_SCENARIO:
        notifyCnt = models.WorkflowExecutionMessages.objects.filter(node_settings_id=node.id, timestamp=timestamp).count()
        if not notifyCnt:
            integromatMsg = 'integromat.error.didNotStart'

    try:
        wem = models.WorkflowExecutionMessages.objects.filter(node_settings_id=node.id, timestamp=timestamp, notified=False).earliest('created')
        integromatMsg = wem.integromat_msg
        wem.notified = True
        wem.save()
    except ObjectDoesNotExist:
        pass

    if integromatMsg:
        notify = True

    return {
        'integromatMsg': integromatMsg,
        'timestamp': timestamp,
        'notify': notify,
        'count': count,
    }

@must_be_valid_project
@must_have_permission(ADMIN)
@must_have_addon(SHORT_NAME, 'node')
def make_register_alternative_webhook_url(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    requestData = request.get_data()
    requestDataJson = json.loads(requestData)

    workflowDescription = requestDataJson['workflowDescription']
    alternativeWebhookUrl = requestDataJson['alternativeWebhookUrl']
    workflowId = 0
    workflows = settings.RDM_WORKFLOW
    for workflow in workflows:
        if ('workflow_description', workflowDescription) in workflow.items():
            try:
                workflowId = workflow['id']
            except KeyError:
                logger.error('The id of workflow is not set.')
                raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        nodeWorkflow, created = models.NodeWorkflows.objects.update_or_create(node_settings_id=addon.id, workflowid=workflowId, defaults={'alternative_webhook_url': alternativeWebhookUrl})

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_info_msg(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    msg = request.json['notifyType']
    timestamp = request.json['timestamp']

    node = models.NodeSettings.objects.get(_id=nodeId)

    wem = models.WorkflowExecutionMessages(
        make_msg=msg,
        timestamp=timestamp,
        node_settings_id=node.id,
    )
    wem.save()

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def make_error_msg(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    nodeId = addon._id

    msg = request.json['notifyType']
    timestamp = request.json['timestamp']

    node = models.NodeSettings.objects.get(_id=nodeId)

    wem = models.WorkflowExecutionMessages(
        integromat_msg=msg,
        timestamp=timestamp,
        node_settings_id=node.id,
    )
    wem.save()

    return {}

@must_be_valid_project
@must_have_permission(READ)
@must_have_addon(SHORT_NAME, 'node')
def make_get_meetings(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)

    tz = pytz.timezone('utc')
    sToday = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
    sYesterday = sToday + timedelta(days=-1)
    sTomorrow = sToday + timedelta(days=1)

    recentMeetings = models.AllMeetingInformation.objects.filter(node_settings_id=addon.id, start_datetime__gte=sYesterday, start_datetime__lt=sTomorrow + timedelta(days=1)).order_by('start_datetime')
    recentMeetingsJson = serializers.serialize('json', recentMeetings, ensure_ascii=False)
    recentMeetingsDict = json.loads(recentMeetingsJson)

    return {
        'recentMeetings': recentMeetingsDict,
    }

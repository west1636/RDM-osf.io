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

def api_create_teams_meeting(requestData, account):

    token = account.oauth_key
    url = '{}{}'.format(settings.MICROSOFT_GRAPH_API_BASE_URL, 'v1.0/me/events')
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)
    response = requests.post(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()
    logger.info('responseData::' + str(responseData))
    return responseData

def grdm_create_teams_meeting(addon, account, createdData):

    subject = createdData['subject']
    organizer = createdData['organizer']['emailAddress']['address']
    startDatetime = createdData['start']['dateTime']
    endDatetime = createdData['end']['dateTime']
    content = createdData['bodyPreview']
    joinUrl = createdData['onlineMeeting']['joinUrl']
    meetingId = createdData['id']
    organizer_fullname = account.display_name

    with transaction.atomic():

        createData = models.MicrosoftTeams(
            subject=subject,
            organizer=organizer,
            organizer_fullname=organizer_fullname,
            start_datetime=startDatetime,
            end_datetime=endDatetime,
            content=content,
            join_url=joinUrl,
            meetingid=meetingId,
            node_settings_id=addon.id,
        )
        createData.save()

    return {}

def api_update_teams_meeting(meetingId, requestData, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.MICROSOFT_GRAPH_API_BASE_URL, 'v1.0/me/events/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)
    response = requests.patch(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()
    logger.info('responseData::' + str(responseData))
    return responseData

def grdm_update_teams_meeting(meetingId, updatedData):

    subject = updatedData['subject']
    startDatetime = updatedData['start']['dateTime']
    endDatetime = updatedData['end']['dateTime']
    content = updatedData['bodyPreview']

    updateData = models.MicrosoftTeams.objects.get(meetingid=meetingId)

    updateData.subject = subject
    updateData.start_datetime = startDatetime
    updateData.end_datetime = endDatetime
    updateData.content = content
    updateData.save()
    logger.info('updateData:::' + str(updateData))

    return {}

def api_delete_teams_meeting(meetingId, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.MICROSOFT_GRAPH_API_BASE_URL, 'v1.0/me/events/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    response = requests.delete(url, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    return {}

def grdm_delete_teams_meeting(meetingId):

    deleteData = models.MicrosoftTeams.objects.get(meetingid=meetingId)
    deleteData.delete()

    return {}

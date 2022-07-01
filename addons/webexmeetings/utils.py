# -*- coding: utf-8 -*-
import json
import requests
from osf.models import ExternalAccount
from addons.webexmeetings import models
from addons.webexmeetings import settings
from django.core import serializers
import logging
from datetime import timedelta
import dateutil.parser
from django.db import transaction
logger = logging.getLogger(__name__)

# widget: ここから
def serialize_webexmeetings_widget(node):
    webexmeetings = node.get_addon('webexmeetings')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': webexmeetings.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(webexmeetings.config.to_json())
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

def api_get_webex_meetings_username(account, email):
    token = account.oauth_key
    url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/people/me')
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=requestHeaders, timeout=60)
    responseData = response.json()
    logger.info('responseData::' +str(responseData))
    username = responseData['displayName']
    return username

def api_create_webex_meeting(requestData, account):

    token = account.oauth_key
    url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/meetings')
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

def grdm_create_webex_meeting(addon, account, createdData):

    subject = createdData['title']
    organizer = createdData['hostEmail']
    startDatetime = createdData['start']
    endDatetime = createdData['end']
    content = createdData['agenda']
    joinUrl = createdData['webLink']
    meetingId = createdData['id']
    password = createdData['password']
    organizer_fullname = account.display_name

    with transaction.atomic():

        createData = models.WebexMeetings(
            subject=subject,
            organizer=organizer,
            organizer_fullname=organizer_fullname,
            start_datetime=startDatetime,
            end_datetime=endDatetime,
            content=content,
            join_url=joinUrl,
            meetingid=meetingId,
            meeting_password=password,
            node_settings_id=addon.id,
        )
        createData.save()

    return {}

def api_update_webex_meeting(meetingId, requestData, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/meetings/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)
    response = requests.put(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()
    logger.info('responseData::' + str(responseData))
    return responseData

def grdm_update_webex_meeting(meetingId, updatedData):

    subject = updatedData['title']
    startDatetime = updatedData['start']
    endDatetime = updatedData['end']
    content = updatedData['agenda']
    meetingId = updatedData['id']

    updateData = models.MicrosoftTeams.objects.get(meetingid=meetingId)

    updateData.subject = subject
    updateData.start_datetime = startDatetime
    updateData.end_datetime = endDatetime
    updateData.content = content
    updateData.save()
    logger.info('updateData:::' + str(updateData))

    return {}

def api_delete_webex_meeting(meetingId, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.WEBEX_API_BASE_URL, '/v1/meetings/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    response = requests.delete(url, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    return {}

def grdm_delete_webex_meeting(meetingId):

    deleteData = models.WebexMeetings.objects.get(meetingid=meetingId)
    deleteData.delete()

    return {}

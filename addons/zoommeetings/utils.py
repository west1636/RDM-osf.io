# -*- coding: utf-8 -*-
import json
import requests
from addons.zoommeetings import models
from addons.zoommeetings import settings
import logging
from datetime import timedelta
import dateutil.parser
from django.db import transaction
logger = logging.getLogger(__name__)

# widget: ここから
def serialize_zoommeetings_widget(node):
    zoommeetings = node.get_addon('zoommeetings')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': zoommeetings.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(zoommeetings.config.to_json())
    return ret
# widget: ここまで

def get_user_info(user_id, jwt_token):

    url = settings.ZOOM_API_URL_USERS + user_id
    payload = {}
    token = 'Bearer ' + jwt_token
    headers = {
        'Authorization': token,
    }

    response = requests.request('GET', url, headers=headers, data=payload)
    status_code = response.status_code
    responseData = response.json()
    userInfo = {}

    if status_code != 200:
        if status_code == 404:
            logger.info('Failed to authenticate Zoom account' + '[' + str(status_code) + ']' + ':' + response.message)
    else:
        userInfo['id'] = responseData['id']
        userInfo['first_name'] = responseData['first_name']
        userInfo['last_name'] = responseData['last_name']

    return userInfo

def api_create_zoom_meeting(requestData, account):

    token = account.oauth_key
    url = '{}{}'.format(settings.ZOOM_API_BASE_URL, 'v2/users/me/meetings')
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)
    response = requests.post(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()
    logger.info('StatusCode:{} . A {} meeting was created with following attributes => '.format(str(response.status_code), settings.ZOOM_MEETINGS) + str(responseData))
    return responseData

def grdm_create_zoom_meeting(addon, account, createdData):

    subject = createdData['topic']
    organizer = createdData['host_email']
    startDatetime = createdData['start_time']
    duration = createdData['duration']
    startDatetime = dateutil.parser.parse(startDatetime)
    endDatetime = startDatetime + timedelta(minutes=duration)
    content = createdData.get('agenda', '')
    joinUrl = createdData['join_url']
    meetingId = createdData['id']
    organizer_fullname = account.display_name

    with transaction.atomic():

        createData = models.Meetings(
            subject=subject,
            organizer=organizer,
            organizer_fullname=organizer_fullname,
            start_datetime=startDatetime,
            end_datetime=endDatetime,
            content=content,
            join_url=joinUrl,
            meetingid=meetingId,
            external_account_id=addon.external_account_id,
            node_settings_id=addon.id,
        )
        createData.save()
    logger.info(' A {} meeting information on GRDM was created with following attributes => '.format(settings.ZOOM_MEETINGS) + str(createData))
    return {}


def api_update_zoom_meeting(meetingId, requestData, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.ZOOM_API_BASE_URL, 'v2/meetings/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)
    response = requests.patch(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    logger.info('StatusCode:{} . A {} meeting was updated with the folloing request body. => '.format(str(response.status_code), settings.ZOOM_MEETINGS) + str(requestBody))
    return {}

def grdm_update_zoom_meeting(meetingId, requestData):

    subject = requestData['topic']
    startDatetime = requestData['start_time']
    duration = requestData['duration']
    startDatetime = dateutil.parser.parse(startDatetime)
    endDatetime = startDatetime + timedelta(minutes=duration)
    content = requestData['agenda']

    updateData = models.Meetings.objects.get(meetingid=meetingId)

    updateData.subject = subject
    updateData.start_datetime = startDatetime
    updateData.end_datetime = endDatetime
    updateData.content = content
    updateData.save()
    logger.info(' A {} meeting information on GRDM was updated with following attributes => '.format(settings.ZOOM_MEETINGS) + str(updateData))
    return {}

def api_delete_zoom_meeting(meetingId, account):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.ZOOM_API_BASE_URL, 'v2/meetings/', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    response = requests.delete(url, headers=requestHeaders, timeout=60)
    if response.status_code != 404:
        response.raise_for_status()
    logger.info('A {} meeting was deleted or has been already deleted. StatusCode : {}=> '.format(settings.ZOOM_MEETINGS) + str(response.status_code))
    return {}

def grdm_delete_zoom_meeting(meetingId):

    deleteData = models.Meetings.objects.get(meetingid=meetingId)
    deleteData.delete()
    logger.info('A {} meeting information on GRDM was deleted.=> '.format(settings.ZOOM_MEETINGS))
    return {}

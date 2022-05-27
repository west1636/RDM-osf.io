# -*- coding: utf-8 -*-
import json
import requests
from osf.models import ExternalAccount
from addons.zoommeetings import models
from addons.zoommeetings import settings
from django.core import serializers
import logging
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

    logger.info(str(responseData))
    logger.info(str(status_code))

    if status_code != 200:
        if status_code == 404:
            logger.info('Failed to authenticate Zoom account' + '[' + str(status_code) + ']' + ':' + message)
    else:
        userInfo['id'] = responseData['id']
        userInfo['first_name'] = responseData['first_name']
        userInfo['last_name'] = responseData['last_name']

    return userInfo

def api_zoom_create_meeting(requestData, account):

    userId = account.oauth_key

    url = settings.ZOOM_API_URL_USERS + 'users' + '/' + userId + '/' + 'meetings'
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, data=requestData, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()

    return responseData

def grdm_create_meeting(node, account, createdData):

    subject = createdData['topic']
    organizer = createdData['host_email']
    startDatetime = createdData['start_time']
    endDatetime = startDatetime + createdData['duration']
    content = createdData['agenda']
    joinUrl = createdData['join_url']
    meetingId = createdData['id']
    host_id = createdData['host_id']
    organizer_fullname = account.display_name

    with transaction.atomic():

        createData = models.ZoomMeetings(
            subject=subject,
            organizer=organizer,
            organizer_fullname=organizer_fullname,
            start_datetime=startDatetime,
            end_datetime=endDatetime,
            content=content,
            join_url=joinUrl,
            meetingid=meetingId,
            node_settings_id=node.id,
        )
        createData.save()

    return {}

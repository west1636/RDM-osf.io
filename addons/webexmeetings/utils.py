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

        createData = models.ZoomMeetings(
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

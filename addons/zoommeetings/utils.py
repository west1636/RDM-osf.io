# -*- coding: utf-8 -*-
import json
import requests
from addons.zoommeetings import settings
from django.core import serializers

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
    token = 'Token ' + jwt_token
    headers = {
        'Authorization': token,
    }

    response = requests.request('GET', url, headers=headers, data=payload)
    status_code = response.status_code
    responseData = response.json()
    userInfo = []

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

# -*- coding: utf-8 -*-
from flask import request
import logging
import json
from addons.webexmeetings import SHORT_NAME
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.webexmeetings.serializer import WebexMeetingsSerializer
from addons.webexmeetings import settings
from osf.models import ExternalAccount, OSFUser
from osf.utils.permissions import WRITE
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from admin.rdm_addons.decorators import must_be_rdm_addons_allowed
from addons.webexmeetings import models
from addons.webexmeetings import utils
from website.oauth.utils import get_service
from requests.exceptions import HTTPError
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
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_request_api(**kwargs):

    auth = kwargs['auth']
    user = auth.user
    requestData = request.get_data()
    requestDataJsonLoads = json.loads(requestData)
    logger.info('{} API will be requested with following attribute by {}=> '.format(settings.WEBEX_MEETINGS, str(user)) + str(requestDataJsonLoads))

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    action = requestDataJsonLoads['actionType']
    updateMeetingId = requestDataJsonLoads['updateMeetingId']
    deleteMeetingId = requestDataJsonLoads['deleteMeetingId']
    guestOrNot = requestDataJsonLoads['guestOrNot']
    requestBody = requestDataJsonLoads['body']

    account = ExternalAccount.objects.get(
        provider='webexmeetings', id=account_id
    )

    if action == 'create':
        try:
            createdMeeting = utils.api_create_webex_meeting(requestBody, account)
            #synchronize data
            utils.grdm_create_webex_meeting(addon, account, createdMeeting, guestOrNot)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = e1.response.status_code if e1.response else e1
            return {
                'errCode': errCode,
            }

    if action == 'update':
        try:
            updatedMeeting = utils.api_update_webex_meeting(updateMeetingId, requestBody, account)
            updatedAttendees = utils.api_update_webex_meeting_attendees(requestDataJsonLoads, account)
            #synchronize data
            utils.grdm_update_webex_meeting(updatedAttendees, updatedMeeting, guestOrNot, addon)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = e1.response.status_code if e1.response else e1
            return {
                'errCode': errCode,
            }

    if action == 'delete':
        try:
            utils.api_delete_webex_meeting(deleteMeetingId, account)
            #synchronize data
            utils.grdm_delete_webex_meeting(deleteMeetingId)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = e1.response.status_code if e1.response else e1
            return {
                'errCode': errCode,
            }

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_register_email(**kwargs):

    auth = kwargs['auth']
    user = auth.user
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    actionType = requestDataJson.get('actionType', '')
    logger.info('{} Email will be {}d with following attribute by {}=> '.format(settings.WEBEX_MEETINGS, str(actionType), str(user)) + str(requestDataJson))

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider=SHORT_NAME, id=account_id
    )
    _id = requestDataJson.get('_id', '')
    guid = requestDataJson.get('guid', '')
    fullname = requestDataJson.get('fullname', '')
    email = requestDataJson.get('email', '')
    is_guest = requestDataJson.get('is_guest', True)
    emailType = requestDataJson.get('emailType', False)
    regType = requestDataJson.get('regType', False)
    displayName = ''
    result = ''
    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)

    if actionType == 'create':
        if is_guest:
            if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, email_address=email, is_guest=is_guest).exists():
                return {
                    'result': 'duplicated_email',
                    'regType': regType,
                }
            if emailType:
                displayName = utils.api_get_webex_meetings_username(account, email)
                if not displayName:
                    return {
                        'result': 'outside_email',
                        'regType': regType,
                    }
            else:
                displayName = fullname
        else:
            if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, external_account_id=account_id, email_address=email, is_guest=is_guest).exists():
                return {
                    'result': 'duplicated_email',
                    'regType': regType,
                }
            fullname = OSFUser.objects.get(guids___id=guid).fullname
            displayName = utils.api_get_webex_meetings_username(account, email)
            if not displayName:
                return {
                    'result': 'outside_email',
                    'regType': regType,
                }
        attendee = models.Attendees(
            user_guid=guid,
            fullname=fullname,
            is_guest=is_guest,
            email_address=email,
            display_name=displayName,
            external_account=None if is_guest else account,
            node_settings=nodeSettings,
        )
        attendee.save()
        logger.info('{} Email was {}d with following attribute by {}=> '.format(settings.WEBEX_MEETINGS, str(actionType), str(user)) + str(vars(attendee)))

    elif actionType == 'update':
        if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, _id=_id).exists():
            attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
            if is_guest:
                if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, email_address=email, is_guest=is_guest).exists():
                    return {
                        'result': 'duplicated_email',
                        'regType': regType,
                    }
                if emailType:
                    displayName = utils.api_get_webex_meetings_username(account, email)
                    if not displayName:
                        return {
                            'result': 'outside_email',
                            'regType': regType,
                        }
                else:
                    if not attendee.is_guest:
                        attendee.user_guid = guid
                        attendee.external_account_id = None
                    displayName = fullname
            else:
                if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, external_account_id=account_id, email_address=email, is_guest=is_guest).exists():
                    return {
                        'result': 'duplicated_email',
                        'regType': regType,
                    }
                attendee.fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname
                displayName = utils.api_get_webex_meetings_username(account, email)
                if not displayName:
                    return {
                        'result': 'outside_email',
                        'regType': regType,
                    }
            attendee.display_name = displayName
            attendee.email_address = email
            attendee.is_guest = is_guest
            attendee.save()

    elif actionType == 'delete':
        attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
        attendee.is_active = False
        attendee.save()
        logger.info('{} Email was {}d with following attribute by {}=> '.format(settings.WEBEX_MEETINGS, str(actionType), str(user)) + str(vars(attendee)))

    newAttendee = {
        'guid': guid,
        'dispName': fullname,
        'fullname': fullname,
        'email': '',
        'institution': '',
        'appUsername': displayName,
        'appEmail': email,
        'profile': '',
        '_id': '',
        'is_guest': is_guest,
    }

    return {
        'result': result,
        'regType': regType,
        'newAttendee': newAttendee,
    }

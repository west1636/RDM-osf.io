# -*- coding: utf-8 -*-
from flask import request
import logging
import requests
import json
import time
import pytz
from datetime import datetime, timedelta
from addons.webexmeetings import SHORT_NAME, FULL_NAME
from django.db import transaction
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.webexmeetings.serializer import WebexMeetingsSerializer
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
from addons.webexmeetings import settings
from addons.webexmeetings import models
from addons.webexmeetings import utils
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from framework.auth.core import Auth
from admin.rdm import utils as rdm_utils
from osf.models import AbstractNode, BaseFileNode, Guid, Comment
from admin.rdm_addons.utils import validate_rdm_addons_allowed
from addons.webexmeetings import SHORT_NAME
from flask import redirect
from website.oauth.utils import get_service
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
    logger.info(str(provider.client_id))
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_request_api(**kwargs):

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
        provider='webexmeetings', id=account_id
    )
    logger.info('requestDataJsonLoads::' +str(requestDataJsonLoads))
    logger.info('requestBody:views::' +str(requestBody))

    if action == 'create':
        createdMeeting = utils.api_create_webex_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_webex_meeting(addon, account, createdMeeting)

    if action == 'update':
        updatedMeeting = utils.api_update_webex_meeting(updateMeetingId, requestBody, account)
        updatedAttendees = utils.api_update_webex_meeting_attendees(requestDataJsonLoads, account)
        #synchronize data
        utils.grdm_update_webex_meeting(updatedAttendees, updatedMeeting, addon)

    if action == 'delete':
        utils.api_delete_webex_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_webex_meeting(deleteMeetingId)

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def webexmeetings_register_email(**kwargs):

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider=SHORT_NAME, id=account_id
    )
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info('Register or Update Web Meeting Email: ' + str(requestDataJson))
    _id = requestDataJson.get('_id', '')
    guid = requestDataJson.get('guid', '')
    fullname = requestDataJson.get('fullname', '')
    email = requestDataJson.get('email', '')
    is_guest = requestDataJson.get('is_guest', True)
    actionType = requestDataJson.get('actionType', '')
    emailType = requestDataJson.get('emailType', False)
    displayName = ''

    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)

    if actionType == 'create':
        if is_guest:
            if emailType:
                displayName = utils.api_get_webex_meetings_username(account, email)
                fullname = fullname if fullname else displayName
        else:
            fullname = OSFUser.objects.get(guids___id=guid).fullname
            displayName = utils.api_get_webex_meetings_username(account, email)

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
    elif actionType == 'update':
        if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, _id=_id).exists():
            attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
            if not is_guest:
                attendee.fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname
                attendee.displayName = utils.api_get_webex_meetings_username(account, email)
            attendee.email_address = email
            attendee.save()
    elif actionType == 'delete':
        attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
        attendee.delete()

    return {}


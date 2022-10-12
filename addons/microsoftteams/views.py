# -*- coding: utf-8 -*-
from flask import request
import logging
import json
from addons.microsoftteams import SHORT_NAME
from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.microsoftteams.serializer import MicrosoftTeamsSerializer
from addons.microsoftteams import settings
from osf.models import ExternalAccount, OSFUser
from osf.utils.permissions import WRITE
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
    must_have_permission,
)
from admin.rdm_addons.decorators import must_be_rdm_addons_allowed
from addons.microsoftteams import models
from addons.microsoftteams import utils
from website.oauth.utils import get_service
from framework.exceptions import HTTPError
logger = logging.getLogger(__name__)

microsoftteams_account_list = generic_views.account_list(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_get_config = generic_views.get_config(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_import_auth = generic_views.import_auth(
    SHORT_NAME,
    MicrosoftTeamsSerializer
)

microsoftteams_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
@must_be_rdm_addons_allowed(SHORT_NAME)
def microsoftteams_oauth_connect(auth, **kwargs):

    provider = get_service(SHORT_NAME)
    authorization_url = provider.get_authorization_url(provider.client_id)

    return authorization_url

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_request_api(**kwargs):

    auth = kwargs['auth']
    user = auth.user
    requestData = request.get_data()
    requestDataJsonLoads = json.loads(requestData)
    logger.info('{} API will be requested with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(user)) + str(requestDataJsonLoads))

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    action = requestDataJsonLoads['actionType']
    updateMeetingId = requestDataJsonLoads['updateMeetingId']
    deleteMeetingId = requestDataJsonLoads['deleteMeetingId']
    requestBody = requestDataJsonLoads['body']
    guestOrNot = requestDataJsonLoads['guestOrNot']

    account = ExternalAccount.objects.get(
        provider='microsoftteams', id=account_id
    )
    if action == 'create':
        createdMeetings = utils.api_create_teams_meeting(requestBody, account)
        #synchronize data
        utils.grdm_create_teams_meeting(addon, account, requestDataJsonLoads, createdMeetings, guestOrNot)

    if action == 'update':
        updatedMeetings = utils.api_update_teams_meeting(updateMeetingId, requestBody, account)
        #synchronize data
        utils.grdm_update_teams_meeting(addon, requestDataJsonLoads, updatedMeetings, guestOrNot)

    if action == 'delete':
        utils.api_delete_teams_meeting(deleteMeetingId, account)
        #synchronize data
        utils.grdm_delete_teams_meeting(deleteMeetingId)

    return {}

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_register_email(**kwargs):

    auth = kwargs['auth']
    user = auth.user
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    actionType = requestDataJson.get('actionType', '')
    logger.info('{} Email will be {}d with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(actionType), str(user)) + str(requestDataJson))

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider='microsoftteams', id=account_id
    )
    _id = requestDataJson.get('_id', '')
    guid = requestDataJson.get('guid', '')
    fullname = requestDataJson.get('fullname', '')
    email = requestDataJson.get('email', '')
    is_guest = requestDataJson.get('is_guest', True)
    emailType = requestDataJson.get('emailType', False)
    displayName = ''
    result = {}
    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)

    if actionType == 'create':
        if is_guest:
            if emailType:
                displayName = utils.api_get_microsoft_username(account, email)
                fullname = fullname if fullname else displayName
        else:
            fullname = OSFUser.objects.get(guids___id=guid).fullname
            displayName = utils.api_get_microsoft_username(account, email)
            if not displayName:
                return 'outside_email'
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
                attendee.display_name = utils.api_get_microsoft_username(account, email)
            attendee.email_address = email
            attendee.save()
    elif actionType == 'delete':
        attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
        attendee.is_active = False
        attendee.save()
    logger.info('{} Email was {}d with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(actionType), str(user)) + str(vars(attendee)))
    return result

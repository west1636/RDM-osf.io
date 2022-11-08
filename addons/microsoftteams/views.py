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
from requests.exceptions import HTTPError
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
        try:
            createdMeetings = utils.api_create_teams_meeting(requestBody, account)
            #synchronize data
            utils.grdm_create_teams_meeting(addon, account, requestDataJsonLoads, createdMeetings, guestOrNot)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = str(e1) if e1.response is None else e1.response.status_code
            return {
                'errCode': errCode,
            }

    if action == 'update':
        try:
            updatedMeetings = utils.api_update_teams_meeting(updateMeetingId, requestBody, account)
            #synchronize data
            utils.grdm_update_teams_meeting(addon, requestDataJsonLoads, updatedMeetings, guestOrNot)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = str(e1) if e1.response is None else e1.response.status_code
            return {
                'errCode': errCode,
            }

    if action == 'delete':
        try:
            utils.api_delete_teams_meeting(deleteMeetingId, account)
            #synchronize data
            utils.grdm_delete_teams_meeting(deleteMeetingId)
        except HTTPError as e1:
            logger.info(str(e1))
            errCode = str(e1) if e1.response is None else e1.response.status_code
            return {
                'errCode': errCode,
            }

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
    has_grdm_account = requestDataJson.get('has_grdm_account', False)
    regAuto = requestDataJson.get('regAuto', False)
    displayName = ''
    result = ''
    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    newAttendee = {}


    if actionType == 'create':
        if regAuto:
            if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, external_account_id=account_id, email_address=email).exists():
                return {
                    'result': 'duplicated_email',
                    'regAuto': regAuto,
                }
        if is_guest:
            displayName = fullname
        else:
            displayName = utils.api_get_microsoft_username(account, email)
            if not displayName:
                return {
                    'result': 'outside_email',
                    'regAuto': regAuto,
                }

        attendee = models.Attendees(
            user_guid=guid,
            fullname=fullname,
            is_guest=is_guest,
            has_grdm_account=has_grdm_account,
            email_address=email,
            display_name=displayName,
            external_account=account,
            node_settings=nodeSettings,
        )
        attendee.save()

        newAttendee = {
            'guid': guid,
            'dispName': fullname,
            'fullname': fullname,
            'email': email,
            'institution': '',
            'appUsername': displayName,
            'appEmail': email,
            'profile': '',
            '_id': '',
            'is_guest': is_guest,
        }

    elif actionType == 'update':
        if models.Attendees.objects.filter(node_settings_id=nodeSettings.id, _id=_id).exists():
            attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)

        if is_guest:
            displayName = fullname
        else:
            displayName = utils.api_get_microsoft_username(account, email)
            if not displayName:
                return {
                    'result': 'outside_email',
                    'regAuto': regAuto,
                }
        if has_grdm_account:
            fullname = OSFUser.objects.get(guids___id=attendee.user_guid).fullname

        attendee.fullname = fullname
        attendee.email_address = email
        attendee.display_name = displayName
        attendee.is_guest = is_guest
        attendee.save()

    elif actionType == 'delete':
        attendee = models.Attendees.objects.get(node_settings_id=nodeSettings.id, _id=_id)
        attendee.is_active = False
        attendee.save()

    logger.info('{} Email was {}d with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(actionType), str(user)) + str(vars(attendee)))

    return {
        'result': result,
        'regAuto': regAuto,
        'newAttendee': newAttendee,
    }

@must_be_valid_project
@must_have_permission(WRITE)
@must_have_addon(SHORT_NAME, 'node')
def microsoftteams_register_contributors_email(**kwargs):

    auth = kwargs['auth']
    user = auth.user
    requestData = request.get_data()
    requestDataJson = json.loads(requestData)
    logger.info('{} Email will be created with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(user)) + str(requestDataJson))

    node = kwargs['node'] or kwargs['project']
    addon = node.get_addon(SHORT_NAME)
    account_id = addon.external_account_id
    account = ExternalAccount.objects.get(
        provider='microsoftteams', id=account_id
    )

    displayName = ''
    result = ''
    nodeSettings = models.NodeSettings.objects.get(_id=addon._id)
    canNotRegister = ''

    for unregisteredContrib in unregisteredContribs:
        guid = requestDataJson.get('guid', '')
        email = requestDataJson.get('email', '')
        fullname = requestDataJson.get('fullname', '')
        try:
            attendee = models.Attendees(
                user_guid=guid,
                fullname=fullname,
                is_guest=True,
                has_grdm_account=True,
                email_address=email,
                display_name=fullname,
                external_account=account,
                node_settings=nodeSettings,
            )
            attendee.save()
            logger.info('{} Email was created with following attribute by {}=> '.format(settings.MICROSOFT_TEAMS, str(user)) + str(vars(attendee)))
        except:
            canNotRegister += fullname
            canNotRegister += ','

    return {
        'canNotRegister': canNotRegister[:-1],
    }

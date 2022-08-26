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
    url = '{}{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/people?email=', email)
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
    logger.info('requestBody::' +str(requestBody))
    logger.info('requestHeaders::' +str(requestHeaders))
    response = requests.post(url, data=requestBody, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    responseData = response.json()
    logger.info('responseData::' + str(responseData))
    return responseData

def get_invitees(account, meetingId):

    token = account.oauth_key
    url = '{}{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/meetingInvitees?meetingId=', meetingId)
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=requestHeaders, timeout=60)
    response.raise_for_status()
    invitees = response.json()
    logger.info('invitees::' + str(invitees))

    return invitees['items']

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

    invitees = get_invitees(account, meetingId)
    attendeeIds = []

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
            external_account_id=addon.external_account_id,
            node_settings_id=addon.id,
        )

        createData.save()

        for invitee in invitees:

            attendeeObj = models.Attendees.objects.get(node_settings_id=addon.id, email_address=invitee['email'])
            attendeeId = attendeeObj.id
            attendeeIds.append(attendeeId)

            relation = models.WebexMeetingsAttendeesRelation(
                attendees_id=attendeeId,
                webex_meetings_id=createData.id,
                webex_meetings_invitee_id=invitee['id']
                )
            relation.save()

        createData.attendees = attendeeIds
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

def grdm_update_webex_meeting(meetingId, requestData, updatedData, addon, account):

    subject = updatedData['title']
    startDatetime = updatedData['start']
    endDatetime = updatedData['end']
    content = updatedData['agenda']
    meetingId = updatedData['id']

    createInvitees = requestData['createInvitees']
    deleteInvitees = requestData['deleteInvitees']

    updateData = models.WebexMeetings.objects.get(meetingid=meetingId)

    updateData.subject = subject
    updateData.start_datetime = startDatetime
    updateData.end_datetime = endDatetime
    updateData.content = content

    token = account.oauth_key
    url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/meetingInvitees/')
    requestToken = 'Bearer ' + token
    requestHeaders = {
        'Authorization': requestToken,
        'Content-Type': 'application/json'
    }
    requestBody = json.dumps(requestData)

    createdInvitees = []
    deletedInvitees = []
    attendeeIdsFormer = []

    logger.info('createInvitees::' + str(createInvitees))
    logger.info('deleteInvitees::' + str(deleteInvitees))

    for createInvitee in createInvitees:
        logger.info('webex1::' + str(createInvitee))
        createInvitee = json.dumps(createInvitee)
        createdResponse = requests.post(url, data=createInvitee, headers=requestHeaders, timeout=60)
        cRes = createdResponse.json()
        createdInvitees.append(cRes)
    for deleteInvitee in deleteInvitees:
        deletedResponse = requests.delete('{}{}'.format(url, deleteInvitee), headers=requestHeaders, timeout=60)
        logger.info('deletedResponse status::' + str(deletedResponse))
        logger.info('deletedResponse status::' + str(deletedResponse.status_code))
        if deletedResponse.ok:
            deletedInvitees.append(deleteInvitee)

    logger.info('createdInvitees::' + str(createdInvitees))
    logger.info('deletedInvitees::' + str(deletedInvitees))

    qsAttendeesRelation = models.WebexMeetingsAttendeesRelation.objects.filter(webex_meetings__meetingid=meetingId)

    for qsAttendeesRelation in qsAttendeesRelation:

        attendeeIdsFormer.append(qsAttendeesRelation.attendees)


    with transaction.atomic():

        for createdInvitee in createdInvitees:

            logger.info('createdInvitee::' + str(createdInvitee))

            craeteRelation = None
            createdAttendeeObj = models.Attendees.objects.get(node_settings_id=addon.id, email_address=createdInvitee['email'])
            craetedAttendeeId = createdAttendeeObj.id
            attendeeIdsFormer.append(craetedAttendeeId)

            craeteRelation = models.WebexMeetingsAttendeesRelation(
                attendees_id=craetedAttendeeId,
                webex_meetings_id=updateData.id,
                webex_meetings_invitee_id=createdInvitee['id']
            )
            craeteRelation.save()

        for deletedInviteeId in deletedInvitees:

            deleteRelation = models.WebexMeetingsAttendeesRelation.objects.get(webex_meetings_invitee_id=deletedInviteeId)
            deletedAttendeeId = deleteRelation.attendees
            attendeeIdsFormer.remove(deletedAttendeeId)
            deleteRelation.delete()
        attendeeIds = attendeeIdsFormer

        updateData.save()
        updateData.attendees = attendeeIds
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

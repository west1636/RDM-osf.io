# -*- coding: utf-8 -*-
import logging

from django.db import models
from osf.models.base import BaseModel, ObjectIDMixin
from addons.base.models import (BaseOAuthNodeSettings, BaseOAuthUserSettings,
                                BaseStorageAddon)
from addons.integromat.serializer import IntegromatSerializer
from addons.integromat.provider import IntegromatProvider

from framework.auth.core import Auth
from osf.utils.fields import EncryptedTextField

logger = logging.getLogger(__name__)

class UserSettings(BaseOAuthUserSettings):
    oauth_provider = IntegromatProvider
    serializer = IntegromatSerializer

class NodeSettings(BaseOAuthNodeSettings, BaseStorageAddon):
    oauth_provider = IntegromatProvider
    serializer = IntegromatSerializer
    user_settings = models.ForeignKey(UserSettings, null=True, blank=True)
    folder_id = models.TextField(blank=True, null=True)
    folder_name = models.TextField(blank=True, null=True)
    folder_location = models.TextField(blank=True, null=True)
    slack_channel_id = models.CharField(max_length=255, default=None, unique=True)

    @property
    def folder_path(self):
        return self.folder_name

    @property
    def display_name(self):
        return u'{0}: {1}'.format(self.config.full_name, self.folder_id)

    def set_folder(self, folder_id, auth):
        # required by superclass, not actually used
        pass

    @property
    def complete(self):
        return bool(self.has_auth and self.user_settings.verify_oauth_access(
            node=self.owner,
            external_account=self.external_account,
        ))

    def authorize(self, user_settings, save=False):
        self.user_settings = user_settings
        self.nodelogger.log(action='node_authorized', save=save)

    def clear_settings(self):
        self.folder_id = None
        self.folder_name = None
        self.folder_location = None

    def deauthorize(self, auth=None, log=True):
        """Remove user authorization from this node and log the event."""
        self.clear_settings()
        self.clear_auth()  # Also performs a save

        if log:
            self.nodelogger.log(action='node_deauthorized', save=True)

    def delete(self, save=True):
        self.deauthorize(log=False)
        super(NodeSettings, self).delete(save=save)

    def serialize_waterbutler_credentials(self):
        # required by superclass, not actually used
        pass

    def serialize_waterbutler_settings(self):
        # required by superclass, not actually used
        pass

    def create_waterbutler_log(self, auth, action, metadata):
        # required by superclass, not actually used
        pass

    def after_delete(self, user):
        self.deauthorize(Auth(user=user), log=True)

class WorkflowExecutionMessages(ObjectIDMixin, BaseModel):

    notified = models.BooleanField(default=False)
    integromat_msg = models.CharField(max_length=255)
    timestamp = models.CharField(max_length=128)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class Attendees(ObjectIDMixin, BaseModel):

    user_guid = models.CharField(max_length=255, default=None)
    fullname = models.CharField(max_length=255)
    microsoft_teams_mail = models.CharField(max_length=254, blank=True, null=True)
    microsoft_teams_user_name = models.CharField(max_length=255, blank=True, null=True)
    webex_meetings_mail = models.CharField(max_length=254, blank=True, null=True)
    webex_meetings_display_name = models.CharField(max_length=255, blank=True, null=True)
    zoom_meetings_mail = models.CharField(max_length=254, blank=True, null=True)
    is_guest = models.BooleanField(default=False)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

    class Meta:
        unique_together = (('user_guid', 'node_settings'), ('microsoft_teams_mail', 'node_settings'), ('webex_meetings_mail', 'node_settings'), ('zoom_meetings_mail', 'node_settings'))


class AllMeetingInformation(ObjectIDMixin, BaseModel):

    subject = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    organizer_fullname = models.CharField(max_length=255)
    attendees = models.ManyToManyField(Attendees, related_name='attendees_meetings')
    attendees_specific = models.ManyToManyField(Attendees, related_name='attendees_specific_meetings', through='AllMeetingInformationAttendeesRelation')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(blank=True, null=True, max_length=255)
    content = models.TextField(blank=True, null=True, max_length=10000)
    join_url = models.TextField(max_length=512)
    meetingid = models.TextField(max_length=512)
    meeting_password = EncryptedTextField(blank=True, null=True)
    appid = models.IntegerField(null=True, blank=True)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class AllMeetingInformationAttendeesRelation(ObjectIDMixin, BaseModel):

    all_meeting_information = models.ForeignKey(AllMeetingInformation)
    attendees = models.ForeignKey(Attendees)
    webex_meetings_invitee_id = models.TextField(blank=True, null=True, max_length=512)

class NodeWorkflows(ObjectIDMixin, BaseModel):

    workflowid = models.IntegerField(null=True, blank=True)
    # An alternative webhook url to the external service
    alternative_webhook_url = EncryptedTextField(blank=True, null=True)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

    class Meta:
        unique_together = (('workflowid', 'node_settings'))

class FileWebappMap(ObjectIDMixin, BaseModel):

    file_guid = models.CharField(max_length=255, default=None, unique=True)
    slack_channel_id = models.CharField(max_length=255, default=None, unique=True)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

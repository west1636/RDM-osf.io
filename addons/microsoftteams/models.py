# -*- coding: utf-8 -*-
import logging

from django.db import models
from osf.models.base import BaseModel, ObjectIDMixin
from addons.base.models import (BaseOAuthNodeSettings, BaseOAuthUserSettings,
                                BaseStorageAddon)
from addons.microsoftteams.serializer import MicrosoftTeamsSerializer
from addons.microsoftteams.provider import MicrosoftTeamsProvider

from framework.auth.core import Auth
from osf.utils.fields import EncryptedTextField

logger = logging.getLogger(__name__)

class UserSettings(BaseOAuthUserSettings):
    oauth_provider = MicrosoftTeamsProvider
    serializer = MicrosoftTeamsSerializer

class NodeSettings(BaseOAuthNodeSettings, BaseStorageAddon):
    oauth_provider = MicrosoftTeamsProvider
    serializer = MicrosoftTeamsSerializer
    user_settings = models.ForeignKey(UserSettings, null=True, blank=True)
    folder_id = models.TextField(blank=True, null=True)
    folder_name = models.TextField(blank=True, null=True)
    folder_location = models.TextField(blank=True, null=True)

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

class MicrosoftTeams(ObjectIDMixin, BaseModel):

    subject = models.CharField(max_length=255)
    organizer = models.CharField(max_length=255)
    organizer_fullname = models.CharField(max_length=255)
    attendees = models.ManyToManyField(Attendees, related_name='attendees_meetings')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    content = models.TextField(blank=True, null=True, max_length=10000)
    join_url = models.TextField(max_length=512)
    meetingid = models.TextField(max_length=512)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class Attendees(ObjectIDMixin, BaseModel):

    user_guid = models.CharField(max_length=255, default=None)
    fullname = models.CharField(max_length=255)
    microsoft_teams_mail = models.CharField(max_length=254, blank=True, null=True)
    microsoft_teams_user_name = models.CharField(max_length=255, blank=True, null=True)
    is_guest = models.BooleanField(default=False)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

    class Meta:
        unique_together = (('user_guid', 'node_settings'), ('microsoft_teams_mail', 'node_settings'))
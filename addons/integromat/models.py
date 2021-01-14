# -*- coding: utf-8 -*-
import logging

from addons.base.models import BaseOAuthNodeSettings, BaseOAuthUserSettings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from osf.models.base import BaseModel
from osf.models.rdm_integromat import RdmWorkflows, RdmWebMeetingApps
from addons.integromat.serializer import IntegromatSerializer

logger = logging.getLogger(__name__)


class IntegromatProvider(object):
    name = 'Integromat'
    short_name = 'integromat'
    serializer = IntegromatSerializer

    def __init__(self, account=None):
        super(IntegromatProvider, self).__init__()  # this does exactly nothing...
        # provide an unauthenticated session by default
        self.account = account

    def __repr__(self):
        return '<{name}: {status}>'.format(
            name=self.__class__.__name__,
            status=self.account.display_name if self.account else 'anonymous'
        )

class UserSettings(BaseOAuthUserSettings):
    oauth_provider = IntegromatProvider
    serializer = IntegromatSerializer

class NodeSettings(BaseOAuthNodeSettings):
    oauth_provider = IntegromatProvider
    serializer = IntegromatSerializer
    user_settings = models.ForeignKey(UserSettings, null=True, blank=True)
    folder_id = models.TextField(blank=True, null=True)
    folder_name = models.TextField(blank=True, null=True)

    @property
    def folder_path(self):
        return self.folder_name

    def serialize_waterbutler_settings(self, *args, **kwargs):
        # required by superclass, not actually used
        pass

    def serialize_waterbutler_credentials(self, *args, **kwargs):
        # required by superclass, not actually used
        pass

    def create_waterbutler_log(self, *args, **kwargs):
        # required by superclass, not actually used
        pass

    def to_json(self, user):

        ret = super(NodeSettings, self).to_json(user)
        user_settings = user.get_addon('integromat')
        ret.update({
            'user_has_auth': user_settings and user_settings.has_auth,
            'is_registration': self.owner.is_registration,
        })

        if self.user_settings and self.user_settings.has_auth:

            owner = self.user_settings.owner

            valid_credentials = True

            ret.update({
                'node_has_auth': True,
                'auth_osf_name': owner.fullname,
                'auth_osf_url': owner.url,
                'valid_credentials': valid_credentials,
            })
        return ret

class Categories(BaseModel):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=128)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class Attendees(BaseModel):
    id = models.AutoField(primary_key=True)
    user_guid = models.CharField(max_length=128)
    microsoft_teams_user_object = models.CharField(max_length=128)
    microsoft_teams_mail = models.CharField(max_length=128)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class Bookmarks(BaseModel):
    id = models.AutoField(primary_key=True)
    workflow = models.ForeignKey(RdmWorkflows, to_field='id', on_delete=models.CASCADE)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

class CategoryWorkflowMap(BaseModel):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Categories, to_field='id', on_delete=models.CASCADE)
    workflow = models.ForeignKey(RdmWorkflows, to_field='id', on_delete=models.CASCADE)
    node_settings = models.ForeignKey(NodeSettings, to_field='_id', on_delete=models.CASCADE)

class AllMeetingInformation(BaseModel):

    id = models.AutoField(primary_key=True)
    subject = models.CharField(blank=True, null=True, max_length=128)
    organizer = models.CharField(max_length=128)
    attendees = ArrayField(models.ForeignKey(Attendees, to_field='id'), default=list, blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    location = models.CharField(blank=True, null=True, max_length=128)
    content = models.CharField(blank=True, null=True, max_length=128)
    join_url = models.CharField(max_length=128)
    meetingid = models.CharField(max_length=128)
    app = models.ForeignKey(RdmWebMeetingApps, to_field='id', on_delete=models.CASCADE)
    node_settings = models.ForeignKey(NodeSettings, null=False, blank=False, default=None)

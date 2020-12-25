# -*- coding: utf-8 -*-
import logging

from addons.base.models import BaseOAuthNodeSettings, BaseOAuthUserSettings
from django.db import models
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

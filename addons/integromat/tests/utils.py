# -*- coding: utf-8 -*-
from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from addons.integromat.tests.factories import IntegromatAccountFactory
from addons.integromat.provider import IntegromatProvider
from addons.integromat.serializer import IntegromatSerializer

class IntegromatAddonTestCase(OAuthAddonTestCaseMixin, AddonTestCase):

    ADDON_SHORT_NAME = 'integromat'
    ExternalAccountFactory = IntegromatAccountFactory
    Provider = IntegromatProvider
    Serializer = IntegromatSerializer
    client = None
    folder = {
        'path': 'bucket',
        'name': 'bucket',
        'id': 'bucket'
    }


# -*- coding: utf-8 -*-
import json
from addons.base.tests.base import OAuthAddonTestCaseMixin, AddonTestCase
from addons.make.tests.factories import MakeAccountFactory
from addons.make.provider import MakeProvider
from addons.make.serializer import MakeSerializer

class MakeAddonTestCase(OAuthAddonTestCaseMixin, AddonTestCase):

    ADDON_SHORT_NAME = 'make'
    ExternalAccountFactory = MakeAccountFactory
    Provider = MakeProvider
    Serializer = MakeSerializer
    client = None
    folder = {
        'path': 'bucket',
        'name': 'bucket',
        'id': 'bucket'
    }

class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code

    def json(self):
        return json.loads(self.content)

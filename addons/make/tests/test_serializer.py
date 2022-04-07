# -*- coding: utf-8 -*-
"""Serializer tests for the My MinIO addon."""
import mock
import pytest

from addons.base.tests.serializers import StorageAddonSerializerTestSuiteMixin
from addons.make.tests.factories import MakeAccountFactory
from addons.make.serializer import MakeSerializer

from tests.base import OsfTestCase

pytestmark = pytest.mark.django_db

class TestMakeSerializer(StorageAddonSerializerTestSuiteMixin, OsfTestCase):
    addon_short_name = 'make'
    Serializer = MakeSerializer
    ExternalAccountFactory = MakeAccountFactory

    def set_provider_id(self, pid):
        self.node_settings.folder_id = pid

    def setUp(self):
        super(TestMakeSerializer, self).setUp()

    def tearDown(self):
        super(TestMakeSerializer, self).tearDown()

# -*- coding: utf-8 -*-

from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory
from osf_tests.factories import ExternalAccountFactory, UserFactory, ProjectFactory

from addons.integromat.models import NodeSettings, UserSettings


class IntegromatAccountFactory(ExternalAccountFactory):
    provider = 'integromat'
    provider_id = Sequence(lambda n: 'id-{0}'.format(n))
    oauth_key = Sequence(lambda n: 'key-{0}'.format(n))
    display_name = 'abc'


class IntegromatUserSettingsFactory(DjangoModelFactory):
    class Meta:
        model = UserSettings

    owner = SubFactory(UserFactory)


class IntegromatNodeSettingsFactory(DjangoModelFactory):
    class Meta:
        model = NodeSettings

    owner = SubFactory(ProjectFactory)
    user_settings = SubFactory(IntegromatUserSettingsFactory)

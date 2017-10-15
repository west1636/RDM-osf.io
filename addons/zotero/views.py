# -*- coding: utf-8 -*-
from flask import request

from .provider import ZoteroCitationsProvider
from website.citations.views import GenericCitationViews
from website.project.decorators import (
    must_have_addon, must_be_addon_authorizer,
    must_have_permission, must_not_be_registration,
    must_be_contributor_or_public
)

class ZoteroViews(GenericCitationViews):
    def set_config(self):
        addon_short_name = self.addon_short_name
        Provider = self.Provider
        @must_not_be_registration
        @must_have_addon(addon_short_name, 'user')
        @must_have_addon(addon_short_name, 'node')
        @must_be_addon_authorizer(addon_short_name)
        @must_have_permission('write')
        def _set_config(node_addon, user_addon, auth, **kwargs):
            """ Changes folder associated with addon.
            Returns serialized node settings
            """
            provider = Provider()
            args = request.get_json()
            external_list_id = args.get('external_list_id')
            external_list_name = args.get('external_list_name')
            external_library_id = args.get('external_library_id', None)
            provider.set_config(
                node_addon,
                auth.user,
                external_list_id,
                external_list_name,
                auth,
                external_library_id
            )
            return {
                'result': provider.serializer(
                    node_settings=node_addon,
                    user_settings=auth.user.get_addon(addon_short_name),
                ).serialized_node_settings
            }
        _set_config.__name__ = '{0}_set_config'.format(addon_short_name)
        return _set_config

    def group_list(self):
        addon_short_name = self.addon_short_name
        Provider = self.Provider
        @must_be_contributor_or_public
        @must_have_addon(addon_short_name, 'node')
        def _group_list(auth, node_addon, **kwargs):
            """ Returns a list of groups - for use with Zotero addon
            """
            return Provider().group_list(node_addon, auth.user)
        _group_list.__name__ = '{0}_group_list'.format(addon_short_name)
        return _group_list

zotero_views = ZoteroViews('zotero', ZoteroCitationsProvider)

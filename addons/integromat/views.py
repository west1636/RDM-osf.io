# -*- coding: utf-8 -*-
from flask import request
import logging
import requests

from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.integromat.serializer import IntegromatSerializer
#from addons.integromat.apps import IntegromatSerializer
from osf.models import ExternalAccount
from django.core.exceptions import ValidationError
from framework.exceptions import HTTPError
from rest_framework import status as http_status
from website.util import api_url_for
from website.project.decorators import (
    must_have_addon,
    must_be_valid_project,
)
from website.ember_osf_web.views import use_ember_app
from website.project import views as project_views
from osf.models.licenses import serialize_node_license_record
from framework.utils import iso8601format
from website.project.model import has_anonymous_link, NodeUpdateError, validate_title
from django.apps import apps
from osf.utils.permissions import ADMIN, READ, WRITE, CREATOR_PERMISSIONS, ADMIN_NODE
from website import settings
from osf.models import Node

logger = logging.getLogger(__name__)

SHORT_NAME = 'integromat'
FULL_NAME = 'Integromat'


integromat_account_list = generic_views.account_list(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_get_config = generic_views.get_config(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_import_auth = generic_views.import_auth(
    SHORT_NAME,
    IntegromatSerializer
)

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

@must_be_logged_in
def integromat_user_config_get(auth, **kwargs):
    """View for getting a JSON representation of the logged-in user's
    Integromat user settings.
    """

    user_addon = auth.user.get_addon('integromat')
    user_has_auth = False
    if user_addon:
        user_has_auth = user_addon.has_auth

    return {
        'result': {
            'userHasAuth': user_has_auth,
            'urls': {
                'create': api_url_for('integromat_add_user_account'),
                'accounts': api_url_for('integromat_account_list'),
            },
        },
    }, http_status.HTTP_200_OK

@must_be_logged_in
def integromat_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    hSdkVersion = '2.0.0'
    try:
        access_token = request.json.get('integromat_api_token')
        webhook_url = request.json.get('integromat_webhook_url')

    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat auth
    if not authIntegromat(access_token, hSdkVersion):
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    user = auth.user

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name=user.username,
            oauth_key=access_token,
            provider_id=webhook_url,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id=webhook_url
        )
        if account.oauth_key != access_token:
            account.oauth_key = access_token
            account.save()

    if not user.external_accounts.filter(id=account.id).exists():

        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    return {}

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

def authIntegromat(access_token, hSdkVersion):

    integromatApiUrl = 'https://api.integromat.com/v1/app'
    authSuccess = False
    token = 'Token ' + access_token
    payload = {}
    headers = {
        'Authorization': token,
        'x-imt-apps-sdk-version': hSdkVersion
    }

    response = requests.request("GET", integromatApiUrl, headers=headers, data=payload)
    authJson = response.json()

    logger.info('integromatLog1::headers' + str(headers))
    logger.info('integromatLog2::' + str(response.text.encode('utf8')))
    logger.info('integromatLog3::' + str(authJson))

    if not type(authJson) is dict :
        authSuccess = True

    logger.info('integromatLog5::' + str(authSuccess))

    return authSuccess

@must_be_valid_project
@must_have_addon('integromat', 'node')
def project_integromat(auth, **kwargs):

    embed_contributors = False
    node = kwargs['node'] or kwargs['project']
    integromat = node.get_addon('integromat')
    user = auth.user
    is_registration = node.is_registration
    parent = node.find_readable_antecedent(auth)
    anonymous = has_anonymous_link(node, auth)
    redirect_url = node.url + '?view_only=None'
    view_only_link = auth.private_key or request.args.get('view_only', '').strip('/')
    NodeRelation = apps.get_model('osf.NodeRelation')
    addons = list(node.get_addons())
    widgets, configs, js, css = project_views.node._render_addons(addons)
    disapproval_link = ''
    if (node.is_pending_registration and node.has_permission(user, ADMIN)):
        disapproval_link = node.root.registration_approval.stashed_urls.get(user._id, {}).get('reject', '')

    ret = {
        'node': {
            'disapproval_link': disapproval_link,
            'id': node._primary_key,
            'title': node.title,
            'category': node.category_display,
            'category_short': node.category,
            'used_quota': ' ',
            'max_quota': ' ',
            'node_type': node.project_or_component,
            'description': node.description or '',
            'license': serialize_node_license_record(node.license),
            'url': node.url,
            'api_url': node.api_url,
            'absolute_url': node.absolute_url,
            'redirect_url': redirect_url,
            'display_absolute_url': node.display_absolute_url,
            'update_url': node.api_url_for('update_node'),
            'is_public': node.is_public,
            'is_archiving': node.archiving,
            'date_created': iso8601format(node.created),
            'date_modified': iso8601format(node.last_logged) if node.last_logged else '',
            'tags': list(node.tags.filter(system=False).values_list('name', flat=True)),
            'children': node.nodes_active.exists(),
            'child_exists': Node.objects.get_children(node, active=True).exists(),
            'is_supplemental_project': node.has_linked_published_preprints,
            'is_registration': is_registration,
            'is_pending_registration': node.is_pending_registration if is_registration else False,
            'is_retracted': node.is_retracted if is_registration else False,
            'is_pending_retraction': node.is_pending_retraction if is_registration else False,
            'retracted_justification': getattr(node.root.retraction, 'justification', None) if is_registration else None,
            'date_retracted': iso8601format(getattr(node.root.retraction, 'date_retracted', None)) if is_registration else '',
            'embargo_end_date': node.embargo_end_date.strftime('%A, %b %d, %Y') if is_registration and node.embargo_end_date else '',
            'is_pending_embargo': node.is_pending_embargo if is_registration else False,
            'is_embargoed': node.is_embargoed if is_registration else False,
            'is_pending_embargo_termination': is_registration and node.is_pending_embargo_termination,
            'registered_from_url': node.registered_from.url if is_registration else '',
            'registered_date': iso8601format(node.registered_date) if is_registration else '',
            'root_id': node.root._id if node.root else None,
            'registered_meta': node.registered_meta,
            'registered_schemas': serialize_meta_schemas(list(node.registered_schema.all())) if is_registration else False,
            'is_fork': node.is_fork,
            'is_collected': node.is_collected,
            'forked_from_id': node.forked_from._primary_key if node.is_fork else '',
            'forked_from_display_absolute_url': node.forked_from.display_absolute_url if node.is_fork else '',
            'forked_date': iso8601format(node.forked_date) if node.is_fork else '',
            'fork_count': node.forks.exclude(type='osf.registration').filter(is_deleted=False).count(),
            'private_links': [x.to_json() for x in node.private_links_active],
            'link': view_only_link,
            'templated_count': node.templated_list.count(),
            'linked_nodes_count': NodeRelation.objects.filter(child=node, is_node_link=True).exclude(parent__type='osf.collection').count(),
            'anonymous': anonymous,
            'comment_level': node.comment_level,
            'has_comments': node.comment_set.exists(),
            'identifiers': {
                'doi': node.get_identifier_value('doi'),
                'ark': node.get_identifier_value('ark'),
            },
            'institutions': project_views.node.get_affiliated_institutions(node) if node else [],
            'access_requests_enabled': node.access_requests_enabled,
            'storage_location': node.osfstorage_region.name,
            'waterbutler_url': node.osfstorage_region.waterbutler_url,
            'mfr_url': node.osfstorage_region.mfr_url,
            'groups': list(node.osf_groups.values_list('name', flat=True)),
        },
        'parent_node': {
            'exists': parent is not None,
            'id': parent._primary_key if parent else '',
            'title': parent.title if parent else '',
            'category': parent.category_display if parent else '',
            'url': parent.url if parent else '',
            'api_url': parent.api_url if parent else '',
            'absolute_url': parent.absolute_url if parent else '',
            'registrations_url': parent.web_url_for('node_registrations', _guid=True) if parent else '',
            'is_public': parent.is_public if parent else '',
            'is_contributor_or_group_member': parent.is_contributor_or_group_member(user) if parent else '',
            'is_contributor': parent.is_contributor(user) if parent else '',
            'can_view': parent.can_view(auth) if parent else False,
        },
        'user': {
            'is_contributor_or_group_member': node.is_contributor_or_group_member(user),
            'is_contributor': node.is_contributor(user),
            'is_admin': node.has_permission(user, ADMIN),
            'is_admin_parent_contributor': parent.is_admin_parent(user, include_group_admin=False) if parent else False,
            'is_admin_parent_contributor_or_group_member': parent.is_admin_parent(user) if parent else False,
            'can_edit': node.has_permission(user, WRITE) and not node.is_registration,
            'can_edit_tags': node.has_permission(user, WRITE),
            'has_read_permissions': node.has_permission(user, READ),
            'permissions': node.get_permissions(user) if user else [],
            'id': user._id if user else None,
            'username': user.username if user else None,
            'fullname': user.fullname if user else '',
            'can_comment': node.can_comment(auth),
            'institutions': project_views.node.get_affiliated_institutions(user) if user else [],
        },
        # TODO: Namespace with nested dicts
        'addons_enabled': [each.short_name for each in addons],
        'addons': configs,
        'addon_widgets': widgets,
        'addon_widget_js': js,
        'addon_widget_css': css,
        'node_categories': [
            {'value': key, 'display_name': value}
            for key, value in settings.NODE_CATEGORY_MAP.items()
        ],
        'has_auth': integromat.has_auth,
        'webhook_url': integromat.external_account.provider_id
    }

    if embed_contributors and not anonymous:
        ret['node']['contributors'] = utils.serialize_visible_contributors(node)
    else:
        ret['node']['contributors'] = list(node.contributors.values_list('guids___id', flat=True))

    return ret

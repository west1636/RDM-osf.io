# -*- coding: utf-8 -*-

import os
import re
import json
import requests
import collections
import unicodedata
import urllib.parse
from django.core import serializers
from django.http.response import JsonResponse
from django.contrib.contenttypes.models import ContentType
from addons.base.utils import get_mfr_url
from osf.models.base import Guid
from osf.models.files import BaseFileNode
from rest_framework import status as http_status
import logging

from flask import request
from django.db.models.expressions import F

from framework.exceptions import HTTPError
from framework.auth.utils import privacy_info_handle
from framework.auth.decorators import must_be_logged_in
from framework.flask import redirect

from addons.wiki.utils import to_mongo_key
from addons.wiki import settings
from addons.wiki import utils as wiki_utils
from addons.wiki.models import WikiPage, WikiVersion
from osf import features
from website import settings as website_settings
from website.files import utils as files_utils
from website.profile.utils import get_profile_image_url
from website.project.views.node import _view_project
from website.project.model import has_anonymous_link
from website.ember_osf_web.decorators import ember_flag_is_active
from website.project.decorators import (
    must_be_contributor_or_public,
    must_have_addon, must_not_be_registration,
    must_be_valid_project,
    must_have_permission,
    must_have_write_permission_or_public_wiki,
    must_not_be_retracted_registration,
)

from osf.exceptions import ValidationError, NodeStateError
from osf.utils.permissions import ADMIN, WRITE
from .exceptions import (
    NameEmptyError,
    NameInvalidError,
    NameMaximumLengthError,
    PageCannotRenameError,
    PageConflictError,
    PageNotFoundError,
    InvalidVersionError,
)

logger = logging.getLogger(__name__)
can_start_import = True

WIKI_NAME_EMPTY_ERROR = HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
    message_short='Invalid request',
    message_long='The wiki page name cannot be empty.'
))
WIKI_NAME_MAXIMUM_LENGTH_ERROR = HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
    message_short='Invalid request',
    message_long='The wiki page name cannot be more than 100 characters.'
))
WIKI_PAGE_CANNOT_RENAME_ERROR = HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
    message_short='Invalid request',
    message_long='The wiki page cannot be renamed.'
))
WIKI_PAGE_CONFLICT_ERROR = HTTPError(http_status.HTTP_409_CONFLICT, data=dict(
    message_short='Page conflict',
    message_long='A wiki page with that name already exists.'
))
WIKI_PAGE_NOT_FOUND_ERROR = HTTPError(http_status.HTTP_404_NOT_FOUND, data=dict(
    message_short='Not found',
    message_long='A wiki page could not be found.'
))
WIKI_INVALID_VERSION_ERROR = HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
    message_short='Invalid request',
    message_long='The requested version of this wiki page does not exist.'
))


def _get_wiki_versions(node, name, anonymous=False):
    # Skip if wiki_page doesn't exist; happens on new projects before
    # default "home" page is created
    wiki_page = WikiPage.objects.get_for_node(node, name)
    if wiki_page:
        versions = wiki_page.get_versions()
    else:
        return []

    return [
        {
            'version': version.identifier,
            'user_fullname': privacy_info_handle(version.user.fullname, anonymous, name=True),
            'date': '{} UTC'.format(version.created.replace(microsecond=0).isoformat().replace('T', ' ')),
        }
        for version in versions
    ]

def _get_wiki_pages_latest(node):
    return [
        {
            'name': page.wiki_page.page_name,
            'url': node.web_url_for('project_wiki_view', wname=page.wiki_page.page_name, _guid=True),
            'wiki_id': page.wiki_page._primary_key,
            'id': page.wiki_page.id,
            'wiki_content': _wiki_page_content(page.wiki_page.page_name, node=node)
        }
        for page in WikiPage.objects.get_wiki_pages_latest(node).order_by(F('name'))
    ]

def _get_wiki_child_pages_latest(node, parent):
    return [
        {
            'name': page.wiki_page.page_name,
            'url': node.web_url_for('project_wiki_view', wname=page.wiki_page.page_name, _guid=True),
            'wiki_id': page.wiki_page._primary_key,
            'id': page.wiki_page.id,
            'wiki_content': _wiki_page_content(page.wiki_page.page_name, node=node)
        }
        for page in WikiPage.objects.get_wiki_child_pages_latest(node, parent).order_by(F('name'))
    ]

def _get_wiki_api_urls(node, name, additional_urls=None):
    urls = {
        'base': node.api_url_for('project_wiki_home'),
        'delete': node.api_url_for('project_wiki_delete', wname=name),
        'rename': node.api_url_for('project_wiki_rename', wname=name),
        'content': node.api_url_for('wiki_page_content', wname=name),
        'settings': node.api_url_for('edit_wiki_settings'),
        'grid': node.api_url_for('project_wiki_grid_data', wname=name)
    }
    if additional_urls:
        urls.update(additional_urls)
    return urls


def _get_wiki_web_urls(node, key, version=1, additional_urls=None):
    urls = {
        'base': node.web_url_for('project_wiki_home', _guid=True),
        'edit': node.web_url_for('project_wiki_view', wname=key, _guid=True),
        'home': node.web_url_for('project_wiki_home', _guid=True),
        'page': node.web_url_for('project_wiki_view', wname=key, _guid=True),
    }
    if additional_urls:
        urls.update(additional_urls)
    return urls


@must_be_valid_project
@must_have_write_permission_or_public_wiki
@must_have_addon('wiki', 'node')
def wiki_page_draft(wname, **kwargs):
    node = kwargs['node'] or kwargs['project']
    wiki_version = WikiVersion.objects.get_for_node(node, wname)

    return {
        'wiki_content': wiki_version.content if wiki_version else None,
        'wiki_draft': (wiki_version.get_draft(node) if wiki_version
                       else wiki_utils.get_sharejs_content(node, wname)),
    }

def _wiki_page_content(wname, wver=None, **kwargs):
    node = kwargs['node'] or kwargs['project']
    wiki_version = WikiVersion.objects.get_for_node(node, wname, wver)
    return {
        'wiki_content': wiki_version.content if wiki_version else '',
        'rendered_before_update': wiki_version.rendered_before_update if wiki_version else False
    }

@must_be_valid_project
@must_be_contributor_or_public
@must_have_addon('wiki', 'node')
def wiki_page_content(wname, wver=None, **kwargs):
    return _wiki_page_content(wname, wver=wver, **kwargs)

@must_be_valid_project  # injects project
@must_have_permission(WRITE)  # injects user, project
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_delete(auth, wname, **kwargs):
    node = kwargs['node'] or kwargs['project']
    wiki_name = wname.strip()
    wiki_page = WikiPage.objects.get_for_node(node, wiki_name)
    sharejs_uuid = wiki_utils.get_sharejs_uuid(node, wiki_name)

    if not wiki_page:
        raise HTTPError(http_status.HTTP_404_NOT_FOUND)

    child_wiki_pages = WikiPage.objects.get_for_node(node=node, parent=wiki_page.id)
    wiki_page.delete(auth)

    if child_wiki_pages:
        for page in child_wiki_pages:
            _child_wiki_delete(auth, node, page)

    wiki_utils.broadcast_to_sharejs('delete', sharejs_uuid, node)
    return {}

def _child_wiki_delete(auth, node, wiki_page):
    wiki_page.delete(auth)
    child_wiki_pages = WikiPage.objects.get_for_node(node=node, parent=wiki_page.id)
    for page in child_wiki_pages:
        _child_wiki_delete(auth, node, page)

@must_be_valid_project  # returns project
@must_be_contributor_or_public
@must_have_addon('wiki', 'node')
@must_not_be_retracted_registration
def project_wiki_view(auth, wname, path=None, **kwargs):
    node = kwargs['node'] or kwargs['project']
    anonymous = has_anonymous_link(node, auth)
    wiki_name = (wname or '').strip()
    wiki_key = to_mongo_key(wiki_name)
    wiki_page = WikiPage.objects.get_for_node(node, wiki_name)
    wiki_version = WikiVersion.objects.get_for_node(node, wiki_name)
    wiki_settings = node.get_addon('wiki')
    parent_wiki_page = WikiPage.objects.get(id=wiki_page.parent) if wiki_page and wiki_page.parent else None
    can_edit = (
        auth.logged_in and not
        node.is_registration and (
            node.has_permission(auth.user, WRITE) or
            wiki_settings.is_publicly_editable
        )
    )
    versions = _get_wiki_versions(node, wiki_name, anonymous=anonymous)

    # Determine panels used in view
    panels = {'view', 'edit', 'compare', 'menu'}
    if request.args and set(request.args).intersection(panels):
        panels_used = [panel for panel in request.args if panel in panels]
        num_columns = len(set(panels_used).intersection({'view', 'edit', 'compare'}))
        if num_columns == 0:
            panels_used.append('view')
            num_columns = 1
    else:
        panels_used = ['view', 'menu']
        num_columns = 1

    try:
        view = wiki_utils.format_wiki_version(
            version=request.args.get('view'),
            num_versions=len(versions),
            allow_preview=True,
        )
        compare = wiki_utils.format_wiki_version(
            version=request.args.get('compare'),
            num_versions=len(versions),
            allow_preview=False,
        )
    except InvalidVersionError:
        raise WIKI_INVALID_VERSION_ERROR

    # ensure home is always lower case since it cannot be renamed
    if wiki_name.lower() == 'home':
        wiki_name = 'home'

    if wiki_version:
        version = wiki_version.identifier
        is_current = wiki_version.is_current
        content = wiki_version.html(node)
        rendered_before_update = wiki_version.rendered_before_update
        markdown = wiki_version.content
    else:
        version = 'NA'
        is_current = False
        content = ''
        rendered_before_update = False
        markdown = ''

    if can_edit:
        if wiki_key not in node.wiki_private_uuids:
            wiki_utils.generate_private_uuid(node, wiki_name)
        sharejs_uuid = wiki_utils.get_sharejs_uuid(node, wiki_name)
    else:
        if not wiki_page and wiki_key != 'home':
            raise WIKI_PAGE_NOT_FOUND_ERROR
        if 'edit' in request.args:
            if wiki_settings.is_publicly_editable:
                raise HTTPError(http_status.HTTP_401_UNAUTHORIZED)
            if node.can_view(auth):
                return redirect(node.web_url_for('project_wiki_view', wname=wname, _guid=True))
            raise HTTPError(http_status.HTTP_403_FORBIDDEN)
        sharejs_uuid = None

    # Opens 'edit' panel when home wiki is empty
    if not content and can_edit and wiki_name == 'home':
        panels_used.append('edit')

    # Default versions for view and compare
    version_settings = {
        'view': view or ('preview' if 'edit' in panels_used else 'current'),
        'compare': compare or 'previous',
    }

    # Get import folder
    root_dir = BaseFileNode.objects.filter(target_object_id=node.id, is_root=True).values('id').first()
    parent_dirs = BaseFileNode.objects.filter(target_object_id=node.id, type='osf.osfstoragefolder', parent=root_dir['id'], deleted__isnull=True)
    import_dirs = []
    for dirr in parent_dirs:
        wiki_dir = BaseFileNode.objects.filter(target_object_id=node.id, type='osf.osfstoragefolder', parent=dirr.id, deleted__isnull=True).first()
        if not wiki_dir:
            continue
        wiki_file_name = wiki_dir.name + '.md'
        if BaseFileNode.objects.filter(target_object_id=node.id, type='osf.osfstoragefile', parent=wiki_dir.id, name=wiki_file_name, deleted__isnull=True).exists():
            dict = {
                'id': dirr._id,
                'name': dirr.name
            }
            import_dirs.append(dict)

    ret = {
        'wiki_id': wiki_page._primary_key if wiki_page else None,
        'wiki_name': wiki_page.page_name if wiki_page else wiki_name,
        'wiki_content': content,
        'wiki_markdown': markdown,
        'parent_wiki_name': parent_wiki_page.page_name if parent_wiki_page else '',
        'import_dirs': import_dirs,
        'rendered_before_update': rendered_before_update,
        'page': wiki_page,
        'version': version,
        'versions': versions,
        'sharejs_uuid': sharejs_uuid or '',
        'sharejs_url': settings.SHAREJS_URL,
        'y_websocket_url': settings.Y_WEBSOCKET_URL,
        'is_current': is_current,
        'version_settings': version_settings,
        'pages_current': _get_wiki_pages_latest(node),
        'category': node.category,
        'panels_used': panels_used,
        'num_columns': num_columns,
        'urls': {
            'api': _get_wiki_api_urls(node, wiki_name, {
                'content': node.api_url_for('wiki_page_content', wname=wiki_name),
                'draft': node.api_url_for('wiki_page_draft', wname=wiki_name),
            }),
            'web': _get_wiki_web_urls(node, wiki_name),
            'profile_image': get_profile_image_url(auth.user, 25),
        },
    }
    ret.update(_view_project(node, auth, primary=True))
    ret['user']['can_edit_wiki_body'] = can_edit
    return ret


@must_be_valid_project  # injects node or project
@must_have_write_permission_or_public_wiki  # injects user
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_edit_post(auth, wname, **kwargs):
    node = kwargs['node'] or kwargs['project']
    # normalize NFC
    wiki_name = unicodedata.normalize('NFC', wname)
    wiki_name = wiki_name.strip()
    wiki_version = WikiVersion.objects.get_for_node(node, wiki_name)
    redirect_url = node.web_url_for('project_wiki_view', wname=wiki_name, _guid=True)
#    form_wiki_content = request.form['content']

    # ensure home is always lower case since it cannot be renamed
    if wiki_name.lower() == 'home':
        wiki_name = 'home'

    requestData = request.get_data()
    getJson = request.get_json()
    form_wiki_content = getJson['markdown']

    # normalize NFC
    form_wiki_content = unicodedata.normalize('NFC', form_wiki_content)

    if wiki_version:
        # Only update wiki if content has changed
        if form_wiki_content != wiki_version.content:
            wiki_version.wiki_page.update(auth.user, form_wiki_content)
            ret = {'status': 'success'}
        else:
            ret = {'status': 'unmodified'}
    else:
        # Create a wiki
        WikiPage.objects.create_for_node(node, wiki_name, form_wiki_content, auth)
        ret = {'status': 'success'}
    return ret, http_status.HTTP_302_FOUND, None, redirect_url

@must_be_valid_project  # injects node or project
@must_have_permission(ADMIN)
@must_not_be_registration
@must_have_addon('wiki', 'node')
def edit_wiki_settings(node, auth, **kwargs):
    wiki_settings = node.get_addon('wiki')
    permissions = request.get_json().get('permission', None)

    if not wiki_settings:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
            message_short='Invalid request',
            message_long='Cannot change wiki settings without a wiki'
        ))

    if permissions == 'public':
        permissions = True
    elif permissions == 'private':
        permissions = False
    else:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
            message_short='Invalid request',
            message_long='Permissions flag used is incorrect.'
        ))

    try:
        wiki_settings.set_editing(permissions, auth, log=True)
    except NodeStateError as e:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
            message_short="Can't change privacy",
            message_long=str(e)
        ))

    return {
        'status': 'success',
        'permissions': permissions,
    }

@must_be_logged_in
@must_be_valid_project
def get_node_wiki_permissions(node, auth, **kwargs):
    return wiki_utils.serialize_wiki_settings(auth.user, [node])

@must_be_valid_project
@must_have_addon('wiki', 'node')
@ember_flag_is_active(features.EMBER_PROJECT_WIKI)
def project_wiki_home(**kwargs):
    node = kwargs['node'] or kwargs['project']
    return redirect(node.web_url_for('project_wiki_view', wname='home', _guid=True))


@must_be_valid_project  # injects project
@must_be_contributor_or_public
@must_have_addon('wiki', 'node')
def project_wiki_id_page(auth, wid, **kwargs):
    node = kwargs['node'] or kwargs['project']
    wiki = WikiPage.objects.get_for_node(node, id=wid)
    if wiki:
        return redirect(node.web_url_for('project_wiki_view', wname=wiki.page_name, _guid=True))
    else:
        raise WIKI_PAGE_NOT_FOUND_ERROR


@must_be_valid_project
@must_have_write_permission_or_public_wiki
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_edit(wname, **kwargs):
    node = kwargs['node'] or kwargs['project']
    return redirect(node.web_url_for('project_wiki_view', wname=wname, _guid=True) + '?edit&view&menu')


@must_be_valid_project
@must_be_contributor_or_public
@must_have_addon('wiki', 'node')
def project_wiki_compare(wname, wver, **kwargs):
    node = kwargs['node'] or kwargs['project']
    return redirect(node.web_url_for('project_wiki_view', wname=wname, _guid=True) + '?view&compare={0}&menu'.format(wver))


@must_not_be_registration
@must_have_permission(WRITE)
@must_have_addon('wiki', 'node')
def project_wiki_rename(auth, wname, **kwargs):
    """View that handles user the X-editable input for wiki page renaming.

    :param wname: The target wiki page name.
    :param-json value: The new wiki page name.
    """
    node = kwargs['node'] or kwargs['project']
    wiki_name = wname.strip()
    new_wiki_name = request.get_json().get('value', None)
    wiki_page = WikiPage.objects.get_for_node(node, wiki_name)

    if not wiki_page:
        raise WIKI_PAGE_NOT_FOUND_ERROR

    try:
        wiki_page.rename(new_wiki_name, auth)
    except NameEmptyError:
        raise WIKI_NAME_EMPTY_ERROR
    except NameInvalidError as error:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
            message_short='Invalid name',
            message_long=error.args[0]
        ))
    except NameMaximumLengthError:
        raise WIKI_NAME_MAXIMUM_LENGTH_ERROR
    except PageCannotRenameError:
        raise WIKI_PAGE_CANNOT_RENAME_ERROR
    except PageConflictError:
        raise WIKI_PAGE_CONFLICT_ERROR
    except PageNotFoundError:
        raise WIKI_PAGE_NOT_FOUND_ERROR
    except ValidationError as err:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST, data=dict(
            message_short='Invalid request',
            message_long=err.messages[0]
        ))
    else:
        sharejs_uuid = wiki_utils.get_sharejs_uuid(node, new_wiki_name)
        wiki_utils.broadcast_to_sharejs('redirect', sharejs_uuid, node, new_wiki_name)


@must_be_valid_project  # returns project
@must_have_permission(WRITE)  # returns user, project
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_validate_name(wname, auth, node, p_wname=None, **kwargs):
    # normalize NFC
    wiki_name = unicodedata.normalize('NFC', wname)
    wiki_name = wiki_name.strip()
    wiki = WikiPage.objects.get_for_node(node, wiki_name)

    if wiki or wiki_name.lower() == 'home':
        raise HTTPError(http_status.HTTP_409_CONFLICT, data=dict(
            message_short='Wiki page name conflict.',
            message_long='A wiki page with that name already exists.'
        ))

    parent_wiki_id = None
    if p_wname:
        p_wname = unicodedata.normalize('NFC', p_wname)
        parent_wiki_name = p_wname.strip()
        parent_wiki = WikiPage.objects.get_for_node(node, parent_wiki_name)
        if not parent_wiki:
            if parent_wiki_name.lower() == 'home':
                # Create a wiki
                parent_wiki = WikiPage.objects.create_for_node(node, parent_wiki_name, '', auth)
            else:
                raise HTTPError(http_status.HTTP_404_NOT_FOUND, data=dict(
                    message_short='Parent Wiki page nothing.',
                    message_long='The parent wiki page does not exist.'
                ))
        parent_wiki_id = parent_wiki.id

    WikiPage.objects.create_for_node(node, wiki_name, '', auth, parent_wiki_id)
    return {'message': wiki_name}

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_grid_data(auth, node, **kwargs):
    pages = []
    project_wiki_pages = {
        'title': 'Project Wiki Pages',
        'kind': 'folder',
        'type': 'heading',
        'children': format_project_wiki_pages(node, auth)
    }
    pages.append(project_wiki_pages)

    component_wiki_pages = {
        'title': 'Component Wiki Pages',
        'kind': 'folder',
        'type': 'heading',
        'children': format_component_wiki_pages(node, auth)
    }
    if len(component_wiki_pages['children']) > 0:
        pages.append(component_wiki_pages)

    return pages


def format_home_wiki_page(node):
    home_wiki = WikiPage.objects.get_for_node(node, 'home')
    home_wiki_page = {
        'page': {
            'url': node.web_url_for('project_wiki_home'),
            'name': 'Home',
            'id': 'None',
        }
    }
    if home_wiki:
        home_wiki_page = {
            'page': {
                'url': node.web_url_for('project_wiki_view', wname='home', _guid=True),
                'name': 'Home',
                'id': home_wiki._primary_key,
            }
        }
        child_wiki_pages = _format_child_wiki_pages(node, home_wiki.id)
        if child_wiki_pages:
            home_wiki_page['children'] = child_wiki_pages
            home_wiki_page['kind'] = 'folder'
    return home_wiki_page


def format_project_wiki_pages(node, auth):
    pages = []
    can_edit = node.has_permission(auth.user, WRITE) and not node.is_registration
    project_wiki_pages = _get_wiki_pages_latest(node)
    home_wiki_page = format_home_wiki_page(node)
    pages.append(home_wiki_page)
    for wiki_page in project_wiki_pages:
        if wiki_page['name'] != 'home':
            has_content = bool(wiki_page['wiki_content'].get('wiki_content'))
            page = {
                'page': {
                    'url': wiki_page['url'],
                    'name': wiki_page['name'],
                    'id': wiki_page['wiki_id'],
                }
            }
            child_wiki_pages = _format_child_wiki_pages(node, wiki_page['id'])
            page['children'] = child_wiki_pages
            if child_wiki_pages:
                page['kind'] = 'folder'

            if can_edit or has_content:
                pages.append(page)
    return pages


def _format_child_wiki_pages(node, parent):
    pages = []
    child_wiki_pages = _get_wiki_child_pages_latest(node, parent)
    if not child_wiki_pages:
        return pages

    for wiki_page in child_wiki_pages:
        if wiki_page['name'] != 'home':
            page = {
                'page': {
                    'url': wiki_page['url'],
                    'name': wiki_page['name'],
                    'id': wiki_page['wiki_id'],
                }
            }
            grandchild_wiki_pages = _format_child_wiki_pages(node, wiki_page['id'])
            page['children'] = grandchild_wiki_pages
            if grandchild_wiki_pages:
                page['kind'] = 'folder'

            pages.append(page)
    return pages


def format_component_wiki_pages(node, auth):
    pages = []
    for node in node.get_nodes(is_deleted=False):
        if any([not node.can_view(auth),
                not node.has_addon('wiki')]):
            continue
        else:
            serialized = serialize_component_wiki(node, auth)
            if serialized:
                pages.append(serialized)
    return pages


def serialize_component_wiki(node, auth):
    children = []
    url = node.web_url_for('project_wiki_view', wname='home', _guid=True)
    home_has_content = bool(_wiki_page_content('home', node=node).get('wiki_content'))
    component_home_wiki = {
        'page': {
            'url': url,
            'name': 'Home',
            # Handle pointers
            'id': node._id
        }
    }
    home_wiki = WikiPage.objects.get_for_node(node, 'home')
    if home_wiki:
        child_wiki_pages = _format_child_wiki_pages(node, home_wiki.id)
        if child_wiki_pages:
            component_home_wiki['children'] = child_wiki_pages
            component_home_wiki['kind'] = 'folder'

    can_edit = node.has_permission(auth.user, WRITE) and not node.is_registration
    if can_edit or home_has_content:
        children.append(component_home_wiki)

    for page in _get_wiki_pages_latest(node):
        if page['name'] != 'home':
            has_content = bool(page['wiki_content'].get('wiki_content'))
            component_page = {
                'page': {
                    'url': page['url'],
                    'name': page['name'],
                    'id': page['wiki_id'],
                }
            }
            child_wiki_pages = _format_child_wiki_pages(node, page['id'])
            component_page['children'] = child_wiki_pages
            if child_wiki_pages:
                component_page['kind'] = 'folder'
            if can_edit or has_content:
                children.append(component_page)

    if len(children) > 0:
        component = {
            'page': {
                'name': node.title,
                'url': url,
            },
            'kind': 'component',
            'category': node.category,
            'pointer': not node.primary,
            'children': children,
        }
        return component
    return None

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_validate_import(dir_id, auth, node, **kwargs):
    global can_start_import 
    can_start_import = True
    import_dir = BaseFileNode.objects.values('id', 'name').get(_id=dir_id)
    import_objects = BaseFileNode.objects.filter(target_object_id=node.id, parent=import_dir['id'], deleted__isnull=True)
    info_list = []
    duplicated_folder_list = []
    for obj in import_objects:
        if obj.type == 'osf.osf.osfstoragefile':
            logger.warn(f'This file cannot be imported: {obj.name}')
            info = {
                'path': import_dir['name'],
                'name': obj.name,
                'status': 'invalid',
                'message': 'This file cannot be imported.',
                'parent_name': None,
            }
            info_list.extend(info)
            continue

        child_info_list = _validate_import_folder(node, obj, '')
        info_list.extend(child_info_list)
    duplicated_folder_list = _validate_import_duplicated_directry(info_list)
    return {
        'data': info_list,
        'duplicated_folder': duplicated_folder_list,
        'canStartImport': can_start_import,
    }

def _validate_import_duplicated_directry(info_list):
    folder_name_list = []
    # create original folder name list
    for info in info_list:
        folder_name_list.append(info['original_name'])
    # extract duplicate page names
    duplicated_folder_list = [k for k, v in collections.Counter(folder_name_list).items() if v > 1]
    return duplicated_folder_list

def _validate_import_folder(node, folder, parent_path):
    index = parent_path.rfind('/')
    parent_wiki_name = parent_path[index+1:] if index != -1 else None
    parent_wiki_fullpath = _get_wiki_fullpath(node, parent_wiki_name)
    p_numbering = None
    # check duplication of parent_wiki_name
    if parent_path != parent_wiki_fullpath:
        p_numbering = _get_wiki_numbering(node, parent_wiki_name)
    if isinstance(p_numbering, int):
        parent_wiki_name = parent_wiki_name + '(' + str(p_numbering) + ')'
        path = parent_path[:index+1] + parent_wiki_name + '/' + folder.name
    else:
        path = parent_path + '/' + folder.name
    info_list = []
    wiki_name = folder.name
    wiki_file_name = folder.name + '.md'
    if not BaseFileNode.objects.filter(target_object_id=node.id, type='osf.osfstoragefile', parent=folder.id, name=wiki_file_name, deleted__isnull=True).exists():
        logger.warn(f'The wiki page does not exist, so the subordinate pages are not processed: {folder.name}')
        info = {
            'path': path,
            'original_name': folder.name,
            'name': folder.name,
            'status': 'invalid',
            'message': 'The wiki page does not exist, so the subordinate pages are not processed.',
        }
        info_list.append(info)
        return info_list

    child_objects = BaseFileNode.objects.filter(target_object_id=node.id, parent=folder.id, deleted__isnull=True)
    for obj in child_objects:
        if obj.type == 'osf.osfstoragefolder':
            child_info_list = _validate_import_folder(node, obj, path)
            info_list.extend(child_info_list)
        else:
            if obj.name == wiki_file_name:
                logger.warn(f'valid wiki page: {obj.name}')
                info = {
                    'parent_wiki_name': parent_wiki_name,
                    'path': path,
                    'original_name': wiki_name,
                    'name': wiki_name,
                    'status': 'valid',
                    'message': '',
                    '_id': obj._id
                }
                info = _validate_import_wiki_exists_duplicated(node, info)
                info_list.append(info)
                continue

                info_list.append(info)
    return info_list

def _validate_import_wiki_exists_duplicated(node, info):
    w_name = info['name']
    p_wname = info['parent_wiki_name']
    if w_name.lower() == 'home':
        return info

    global can_start_import
    # get wiki full path
    fullpath = _get_wiki_fullpath(node, w_name)
    wiki = WikiPage.objects.get_for_node(node, w_name)
    if wiki:
        if fullpath == info['path']:
            # if the wiki exists, update info list
            info['status'] = 'valid_exists'
            info['numbering'] = _get_wiki_numbering(node, w_name)
            can_start_import = False
        else:
            # if the wiki duplicated, update info list
            info['status'] = 'valid_duplicated'
            info['numbering'] = _get_wiki_numbering(node, w_name)
            info['name'] = info['name'] + '(' + str(info['numbering']) + ')'
            info['path'] = info['path'] + '(' + str(info['numbering']) + ')'
            can_start_import = False
    return info

def _get_wiki_parent(wiki, path):
    try:
        parent_wiki_page = WikiPage.objects.get(id=wiki.parent)
        path = parent_wiki_page.page_name + '/' + path
        return _get_wiki_parent(parent_wiki_page, path)
    except:
        return path

def _get_wiki_fullpath(node, w_name):
    wiki = WikiPage.objects.get_for_node(node, w_name)
    if wiki is None:
        return ''
    fullpath = '/' + _get_wiki_parent(wiki, w_name)
    return fullpath

def _get_wiki_numbering(node, w_name):
    max = 1000
    index = 1
    wiki = WikiPage.objects.get_for_node(node, w_name)
    if wiki is None:
        return ''

    for index in range(index, max+1):
        wiki = WikiPage.objects.get_for_node(node, w_name + '('+ str(index) + ')')
        if wiki is None:
            return index
    return None

def get_node_guid(node):

    qsGuid = node._prefetched_objects_cache['guids'].only()
    guidSerializer = serializers.serialize('json', qsGuid, ensure_ascii=False)
    guidJson = json.loads(guidSerializer)
    guid = guidJson[0]['fields']['_id']
    return guid

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_copy_import_directory(dir_id, auth, node, **kwargs):
    logger.info('copy import directory start')
    data = request.get_json()
    folderPath = data['folderPath']
    copyFrom_id = dir_id
    toCopy_id = folderPath[1:][:-1]
    copyFrom = BaseFileNode.objects.get(_id=copyFrom_id)
    toCopy = BaseFileNode.objects.get(_id=toCopy_id)

    cloned = files_utils.copy_files(copyFrom, node, toCopy)
    cloned_id = cloned._id
    logger.info('copy import directory end')
    return {'clonedId': cloned_id}

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_replace(dir_id, auth, node, **kwargs):
    logger.info('------------replace md start------------')
    data = request.get_json()
    wiki_info = data['wiki_info']
    replaced_wiki_info = []
    repLink = r'(?<!\\)\[(?P<title>.+?(?<!\\)(?:\\\\)*)\]\((?P<path>.+?)(?<!\\)\)'
    repImage = r'(?<!\\)!\[(?P<title>.+?(?<!\\)(?:\\\\)*)\]\((?P<path>.+?)(?<!\\)\)'
    all_children_name = _get_all_wiki_name_import_directory(dir_id)
    for info in wiki_info:
        wiki_content = info['wiki_content']
        linkMatches = list(re.finditer(repLink, wiki_content))
        imageMatches = list(re.finditer(repImage, wiki_content))
        info['wiki_content'] = _replace_wiki_image(node, imageMatches, wiki_content, info, dir_id)
        info['wiki_content'] = _replace_wiki_link_notation(node, linkMatches, info['wiki_content'], info, all_children_name, dir_id)
        replaced_wiki_info.append(info)
    logger.info('------------replace md end------------')
    return {'replaced': replaced_wiki_info}

def _get_all_wiki_name_import_directory(dir_id):

    import_directory_root = BaseFileNode.objects.get(_id=dir_id)
    children = import_directory_root._children.filter(type='osf.osfstoragefolder', deleted__isnull=True)
    all_dir_list = []
    for child in children:
        all_dir_list.append(child.name)
        all_child_list = _get_all_child_directory(child._id)
        all_dir_list.extend(all_child_list)
    return all_dir_list

def _get_all_child_directory(dir_id):
    parent_dir = BaseFileNode.objects.get(_id=dir_id)
    children = parent_dir._children.filter(type='osf.osfstoragefolder', deleted__isnull=True)
    dir_list = []
    for child in children:
        dir_list.append(child.name)
        child_list = _get_all_child_directory(child._id)
        dir_list.extend(child_list)

    return dir_list

def _replace_wiki_link_notation(node, linkMatches, wiki_content, info, all_children_name, dir_id):
    wiki_name = info['wiki_name']
    for match in linkMatches:
        hasSharp = '#' in match['path']
        hasDot = '.' in match['path']
        repUrl = r"^https?://[\w/:%#\$&\?\(\)~\.=\+\-]+$"
        isUrl = re.match(repUrl, match['path'])
        if bool(isUrl):
            continue
        if hasSharp:
            if hasDot:
                # relace file name
                wiki_content = _replace_file_name(node, wiki_name, wiki_content, match, 'link', dir_id)
                continue
            continue

        # check whether wiki or not
        isWiki = _check_wiki_name_exist(node, match['path'], all_children_name)
        if isWiki:
            wiki_content = wiki_content.replace('[' + match['title'] + '](' + match['path'] + ')', '[' + match['title'] + '](../' + match['path'] + '/)')
        else:
            # If not wiki, check whether attachment file or not
            wiki_content = _replace_file_name(node, wiki_name, wiki_content, match, 'link', dir_id)

    return wiki_content

def _check_wiki_name_exist(node, checkedName, all_children_name):
    replaced_wiki_name = _replace_common_rule(checkedName)
    # normalize NFC
    replaced_wiki_name = unicodedata.normalize('NFC', replaced_wiki_name)
    wiki = WikiPage.objects.get_for_node(node, replaced_wiki_name)
    if wiki:
        return True
    else:
        # check import directory(copyed)
        for name in all_children_name:
            if replaced_wiki_name == name:
                return True
    return False

def _replace_file_name(node, wiki_name, wiki_content, match, notation, dir_id):
    # check whether attachment file or not
    file_id = _check_attachment_file_name_exist(wiki_name, match['path'], dir_id)
    if file_id:
        # replace process of file name
        node_guid = get_node_guid(node)
        if notation == 'image':
            url = website_settings.WATERBUTLER_URL + '/v1/resources/' +  node_guid + '/providers/osfstorage/' + file_id + '?mode=render'
            wiki_content = wiki_content.replace('![' + match['title'] + '](' + match['path'] + ')', '![' + match['title'] + '](' + url + ')')
        elif notation == 'link':
            file_obj = BaseFileNode.objects.get(_id=file_id)
            url = website_settings.DOMAIN + node_guid + '/files/osfstorage/' + file_id
        wiki_content = wiki_content.replace('[' + match['title'] + '](' + match['path'] + ')', '[' + match['title'] + '](' + url + ')')
    return wiki_content

def _check_attachment_file_name_exist(wiki_name, file_name, dir_id):
    # check file name contains slash
    hasHat = '^' in file_name
    if hasHat:
        another_wiki_name = file_name.split('^')[0]
        file_name = file_name.split('^')[1]
        # check as wikiName/fileName
        file_id = _process_attachment_file_name_exist(hasHat, another_wiki_name, file_name, dir_id)
    else:
        # check as fileName
        file_id = _process_attachment_file_name_exist(hasHat, wiki_name, file_name, dir_id)

    return file_id

def _process_attachment_file_name_exist(hasHat, wiki_name, file_name, dir_id):
    # check as fileName
    replaced_wiki_name = _replace_common_rule(wiki_name) if hasHat else wiki_name
    replaced_file_name = _replace_common_rule(file_name)

    parent_directory = _get_wiki_import_directory(replaced_wiki_name, dir_id)
    try:
        # normalize NFC
        replaced_file_name = unicodedata.normalize('NFC', replaced_file_name)
        child_file = parent_directory._children.get(name=replaced_file_name, type='osf.osfstoragefile', deleted__isnull=True)
        return child_file._id
    except:
        logger.info('---NG---')
        pass

    return None

def _get_wiki_import_directory(wiki_name, dir_id):
    import_directory_root = BaseFileNode.objects.get(_id=dir_id)
    children = import_directory_root._children.filter(type='osf.osfstoragefolder', deleted__isnull=True)
    # normalize NFC
    wiki_name = unicodedata.normalize('NFC', wiki_name)
    for child in children:
        if child.name == wiki_name:
            return child
        wiki = _get_wiki_import_directory(wiki_name, child._id)
        if wiki:
            return wiki
    return None

def _replace_wiki_image(node, imageMatches, wiki_content, wiki_info, dir_id):
    wiki_name = wiki_info['wiki_name']
    for match in imageMatches:
        wiki_content = _replace_file_name(node, wiki_name, wiki_content, match, 'image', dir_id)
    return wiki_content

# for Search wikiName or fileName
def _replace_common_rule(name):
    hasPlus = '+' in name
    # decode
    if hasPlus:
        decodedName = urllib.parse.unquote_plus(name)
    else:
        decodedName = urllib.parse.unquote(name)
    return decodedName

@must_be_valid_project  # returns project
@must_have_permission(WRITE)  # returns user, project
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_import_process(wname, auth, node, p_wname=None, **kwargs):
    parent_wiki_id = None
    dataJson = request.get_json()
    data = dataJson['wikiContent']
    # normalize NFC
    data = unicodedata.normalize('NFC', data)
    wiki_name = unicodedata.normalize('NFC', wname)

    ret = {'status_or_error_wiki_name': wiki_name}
    if p_wname:
        p_wname = unicodedata.normalize('NFC', p_wname)
        parent_wiki_name = p_wname.strip()
        parent_wiki = WikiPage.objects.get_for_node(node, parent_wiki_name)
        if not parent_wiki:
            raise HTTPError(http_status.HTTP_404_NOT_FOUND, data=dict(
                message_short='Parent Wiki page nothing.',
                message_long='The parent wiki page does not exist.',
                error_wiki_name=wiki_name
            ))
        parent_wiki_id = parent_wiki.id

    wiki_version = WikiVersion.objects.get_for_node(node, wiki_name)
    # ensure home is always lower case since it cannot be renamed
    if wiki_name.lower() == 'home':
        wiki_name = 'home'

    if wiki_version:
        # Only update wiki if content has changed
        if data != wiki_version.content:
            wiki_version.wiki_page.update(auth.user, data)
            ret = {'status_or_error_wiki_name': 'success'}
        else:
            ret = {'status_or_error_wiki_name': 'unmodified'}
    else:
        # Create a wiki
        WikiPage.objects.create_for_node(node, wiki_name, data, auth, parent_wiki_id)
        ret = {'status_or_error_wiki_name': 'success'}

    return ret

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_get_imported_wiki_workspace(dir_id, auth, node, **kwargs):
    imported_wiki_workspace_folder_name = 'Imported Wiki workspace (temporary)'
    try:
        wiki_images_dir = BaseFileNode.objects.get(_id=dir_id)
    except:
        raise HTTPError(http_status.HTTP_404_NOT_FOUND, data=dict(
            message_short='Wiki images folder nothing.',
            message_long='Wiki images folder does not exist.'
        ))
    try:
        imported_wiki_workspace_folder = wiki_images_dir._children.get(name=imported_wiki_workspace_folder_name, type='osf.osfstoragefolder', deleted__isnull=True)
        path = '/' + imported_wiki_workspace_folder._id + '/'
        exist = True
    except:
        # if NOT exist, return Wiki images dir_id
        path = '/' + dir_id +'/'
        exist = False

    return {'path': path, 'exist': exist}

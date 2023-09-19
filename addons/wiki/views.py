# -*- coding: utf-8 -*-

import os
import re
import json
import requests
import collections
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
    wiki_name = wname.strip()
    wiki_version = WikiVersion.objects.get_for_node(node, wiki_name)
    redirect_url = node.web_url_for('project_wiki_view', wname=wiki_name, _guid=True)
#    form_wiki_content = request.form['content']

    # ensure home is always lower case since it cannot be renamed
    if wiki_name.lower() == 'home':
        wiki_name = 'home'

    requestData = request.get_data()
    logger.info('requestGetJson:::' + str(request.get_json))
    getJson = request.get_json()
    form_wiki_content = getJson['markdown']
    logger.info('form_wiki_content:::' + str(form_wiki_content))

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
    wiki_name = wname.strip()
    wiki = WikiPage.objects.get_for_node(node, wiki_name)

    if wiki or wiki_name.lower() == 'home':
        raise HTTPError(http_status.HTTP_409_CONFLICT, data=dict(
            message_short='Wiki page name conflict.',
            message_long='A wiki page with that name already exists.'
        ))

    parent_wiki_id = None
    if p_wname:
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

#        child_info_list = _validate_import_folder(node, obj, import_dir['name'])
        child_info_list = _validate_import_folder(node, obj, '')
        info_list.extend(child_info_list)
    duplicated_folder_list = _validate_import_duplicated_directry(info_list)
#    logger.info(info_list)
#    logger.info(duplicated_folder_list)
#    logger.info(can_start_import)
    return {
        'data': info_list,
        'duplicated_folder': duplicated_folder_list,
        'canStartImport': can_start_import,
    }

def _validate_import_duplicated_directry(info_list):
    folder_name_list = []
    # create original folder name list
    for info in info_list:
        # pick up md
        if os.path.splitext(os.path.basename(info['original_name']))[1][1:] == 'md':
            folder_name_list.append(info['original_name'])
    # extract duplicate page names
    duplicated_folder_list = [k for k, v in collections.Counter(folder_name_list).items() if v > 1]
    return duplicated_folder_list

def _validate_import_folder(node, folder, parent_path):
    logger.info('--validateimportfolder----')
    logger.info('parent_path:  ' +str(parent_path))
    index = parent_path.rfind('/')
    logger.info(index)
    parent_wiki_name = parent_path[index+1:] if index != -1 else None
    logger.info('parent_wiki_name:  ' +str(parent_wiki_name))
    path = parent_path + '/' + folder.name
    info_list = []
    VALID_IMG_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
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
                    'original_name': obj.name,
                    'name': obj.name,
                    'status': 'valid',
                    'message': '',
                    '_id': obj._id
                }
                info = _validate_import_wiki_exists_duplicated(node, info)
                info_list.append(info)
                continue

            ext = os.path.splitext(obj.name)[-1].lower()
            if ext not in VALID_IMG_EXTENSIONS:
                logger.warn(f'Only image files can be imported: {obj.name}')
                info = {
                    'path': path,
                    'original_name': obj.name,
                    'name': obj.name,
                    'status': 'invalid',
                    'message': 'Only image files can be imported.',
                }
                info_list.append(info)
    return info_list

def _validate_import_wiki_exists_duplicated(node, info):
    logger.info('---validateimportwikiexistsduplicated---')
    w_name = info['name'].rstrip('.md')
    logger.info(w_name)
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
            can_start_import = False
        else:
            # if the wiki duplicated, update info list
            info['status'] = 'valid_duplicated'
            info['name'] += '(1)'
            can_start_import = False
#            info['path'] = re.sub(info['original_name'] + r'(?!.+' + info['original_name'] + ')', info['name'], info['path'], flags=re.DOTALL)
    return info

def _get_wiki_fullpath(node, w_name):
    wiki = WikiPage.objects.get_for_node(node, w_name)
    if wiki is None:
        return ''
    fullpath = '/' + _get_wiki_parent(wiki, w_name)
    return fullpath

def _get_wiki_parent(wiki, path):
    try:
        parent_wiki_page = WikiPage.objects.get(id=wiki.parent)
        path = parent_wiki_page.page_name + '/' + path
        return _get_wiki_parent(parent_wiki_page, path)
    except:
        return path

def get_node_guid(node):

    qsGuid = node._prefetched_objects_cache['guids'].only()
    guidSerializer = serializers.serialize('json', qsGuid, ensure_ascii=False)
    guidJson = json.loads(guidSerializer)
    guid = guidJson[0]['fields']['_id']
    return guid

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_copy_import_directory(dir_id, auth, node, **kwargs):
    logger.info('copy import directory startaaa')
    data = request.get_json()
    wiki_info = data['validationResult']
    folderPath = data['folderPath']
    logger.info(folderPath)
    logger.info(wiki_info)
    copyFrom_id = dir_id
    toCopy_id = folderPath[1:][:-1]
    logger.info(copyFrom_id)
    logger.info(toCopy_id)
    copyFrom = BaseFileNode.objects.get(_id=copyFrom_id)
    toCopy = BaseFileNode.objects.get(_id=toCopy_id)

    cloned = files_utils.copy_files(copyFrom, node, toCopy)
    cloned_id = cloned._id
    logger.info(cloned_id)
#    url = http://localhost:7777/v1/resources/ed6b4/providers/osfstorage/64fec6466788154b7d63be5d/
    logger.info('copy import directory end')
    return {'clonedId': cloned_id}

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_replace(dir_id, auth, node, **kwargs):
    logger.info('------------replace md start------------')
    data = request.get_json()
    wiki_info = data['wiki_info']
    logger.info(wiki_info)
    replaced_wiki_info = []
#    repLink = r"\[(.+?)\]\(([a-zA-Z0-9-._~:/?#@!$&'()*+,;=%]+)\)"
#    repLink = r"\[(.+?)\]\(([a-zA-Z0-9-._~:/?#@!$&'()*+,;=%\w]+)\)"
#    repImage = r"!\[(.*?)\]\(([a-zA-Z0-9-._~:/?#@!$&'()*+,;=%\w]+)\)"
#    repLink = r"\[(.+?)\]\((.+?)\)"
#    repImage = r"!\[(.*?)\]\((.+?)\)"
    repLink = r"\[((?!.*\\$).+)\]\(((?!.*\\$).+)\)"
    repImage = r"!\[((?!.*\\$).*)\]\(((?!.*\\$).+)\)"
    all_children_name = _get_all_wiki_name_import_directory(dir_id)
    for info in wiki_info:
        if info['validation'] == 'valid':
            wiki_content = info['wiki_content']
            linkMatches = re.findall(repLink, wiki_content)
            imageMatches = re.findall(repImage, wiki_content)
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
    logger.info('------------_replace_wiki_link_notation start------------')
    # remove '.md'
    wiki_name, ext = os.path.splitext(info['wiki_name'])
    for match in linkMatches:
        hasSharp = '#' in match[1]
        hasDot = '.' in match[1]
        repUrl = r"^https?://[\w/:%#\$&\?\(\)~\.=\+\-]+$"
        isUrl = re.match(repUrl, match[1])
        if bool(isUrl):
            continue
        if hasSharp:
            if hasDot:
                # relace file name
                logger.info('---has # and likely to FILE---')
                wiki_content = _replace_file_name(node, wiki_name, wiki_content, match[1], 'link', dir_id)
                continue

        # check whether wiki or not
        isWiki = _check_wiki_name_exist(node, match[1], all_children_name)
        if isWiki:
            # replace wiki name
            wiki_content = wiki_content.replace('](' + match[1] + ')', '](../' + match[1] + '/)')
        else:
            # If not wiki, check whether attachment file or not
            logger.info('---it is not WIKI, likely to FILE---')
            wiki_content = _replace_file_name(node, wiki_name, wiki_content, match[1], 'link', dir_id)

    return wiki_content

def _check_wiki_name_exist(node, checkedName, all_children_name):
    logger.info('------------_check_wiki_name_exist start------------')
    # check existing wiki
    # Need [%20],[%23],[\(],[\)] is to be replaced in checkedName
    replaced_wiki_name = _replace_common_rule(checkedName)
    wiki = WikiPage.objects.get_for_node(node, replaced_wiki_name)
    if wiki:
        return True
    else:
        # check import directory(copyed)
        for name in all_children_name:
            if replaced_wiki_name == name:
                return True
    return False

def _replace_file_name(node, wiki_name, wiki_content, file_name, notation, dir_id):
    logger.info('------------_replace_file_name start------------')
    # check whether attachment file or not
    file_id = _check_attachment_file_name_exist(wiki_name, file_name, dir_id)
    if file_id:
        # replace process of file name
        #renderUrl = http://localhost:7777/v1/resources/y39bz/providers/osfstorage/64f9604f224f72001089b9de?mode=render
        node_guid = get_node_guid(node)
        if notation == 'image':
            url = website_settings.WATERBUTLER_URL + '/v1/resources/' +  node_guid + '/providers/osfstorage/' + file_id + '?mode=render'
        elif notation == 'link':
            file_obj = BaseFileNode.objects.get(_id=file_id)
            url = website_settings.DOMAIN + node_guid + '/files/osfstorage/' + file_id
        wiki_content = wiki_content.replace('](' + file_name + ')', '](' + url + ')')
    else:
        logger.info('---DO NOT REPLACE----')
    return wiki_content

def _check_attachment_file_name_exist(wiki_name, file_name, dir_id):
    logger.info('------------_check_attachment_file_name_exist start------------')
    # check file name contains slash
#    hasSlash = '/' in file_name
    hasHat = '\^' in file_name
#    if hasSlash:
    if hasHat:
        another_wiki_name = file_name.split('\^')[0]
        file_name = file_name.split('\^')[1]
        # check as wikiName/fileName
        file_id = _process_attachment_file_name_exist(another_wiki_name, file_name, dir_id)
        logger.info(file_name)
        logger.info(file_id)
    else:
        # check as fileName
        file_id = _process_attachment_file_name_exist(wiki_name, file_name, dir_id)

    return file_id

def _process_attachment_file_name_exist(wiki_name, file_name, dir_id):
    logger.info('------------_process_attachment_file_name_exist start------------')
    # check as fileName
    # Need [%20],[%23],[\(],[\)] is to be replaced in wiki_name and file_name
    replaced_wiki_name = _replace_common_rule(wiki_name)
    replaced_file_name = _replace_common_rule(file_name)

    parent_directory = _get_wiki_import_directory(replaced_wiki_name, dir_id)
    try:
        logger.info(replaced_file_name)
        child_file = parent_directory._children.get(name=replaced_file_name, type='osf.osfstoragefile', deleted__isnull=True)
        return child_file._id
    except:
        logger.info(replaced_file_name)
        logger.info('---NG---')
        pass

    return None

def _get_wiki_import_directory(wiki_name, dir_id):
    logger.info('------------_get_wiki_import_directory start------------')
    import_directory_root = BaseFileNode.objects.get(_id=dir_id)
    children = import_directory_root._children.filter(type='osf.osfstoragefolder', deleted__isnull=True)
    for child in children:
        if child.name == wiki_name:
            return child
        wiki = _get_wiki_import_directory(wiki_name, child._id)
        if wiki:
            return wiki
    return None

def _replace_wiki_image(node, imageMatches, wiki_content, wiki_info, dir_id):
    logger.info('------------_replace_wiki_image start------------')
    # remove '.md'
    wiki_name, ext = os.path.splitext(wiki_info['wiki_name'])
    for match in imageMatches:
        wiki_content = _replace_file_name(node, wiki_name, wiki_content, match[1], 'image', dir_id)
    return wiki_content

# for Search wikiName or fileName
def _replace_common_rule(name):
    logger.info('------------replacecommonrule start------------')
    replaceName = name
    logger.info(replaceName)
    # Need [%20],[%23],[\(],[\)] [\\] is to be replaced in file_name
    replaceRule = [['%20', ' '], ['%23', '#'], ['\(', '('], ['\)', ')'], ['\\', '']]
    for toReplace in replaceRule:
        replaceName = replaceName.replace(toReplace[0], toReplace[1])
    logger.info(replaceName)
    return replaceName

@must_be_valid_project  # returns project
@must_have_permission(WRITE)  # returns user, project
@must_not_be_registration
@must_have_addon('wiki', 'node')
def project_wiki_import_process(wname, auth, node, p_wname=None, **kwargs):
    logger.info('---projectwikiimportprocess--- start')
    # remove '.md'
    wiki_name, ext = os.path.splitext(wname)
    parent_wiki_id = None
    wiki = WikiPage.objects.get_for_node(node, wiki_name)
    data = request.get_data()
    logger.info(wname)

    if p_wname:
        parent_wiki_name = p_wname.strip()
        parent_wiki = WikiPage.objects.get_for_node(node, parent_wiki_name)
        if not parent_wiki:
            raise HTTPError(http_status.HTTP_404_NOT_FOUND, data=dict(
                message_short='Parent Wiki page nothing.',
                message_long='The parent wiki page does not exist.'
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
            ret = {'status': 'success'}
        else:
            ret = {'status': 'unmodified'}
    else:
        # Create a wiki
        WikiPage.objects.create_for_node(node, wiki_name, data, auth, parent_wiki_id)

    logger.info('---projectwikiimportprocess end---')
#    WikiPage.objects.create_for_node(node, wiki_name, data, auth, parent_wiki_id)
    return {'message': [], 'error_wiki_name': []}

@must_be_valid_project
@must_be_contributor_or_public
def project_wiki_get_imported_wiki_workspace(dir_id, auth, node, **kwargs):
    logger.info('---getimportedwikiworkspace--- start')
    imported_wiki_workspace_folder_name = 'Imported Wiki workspace (temporary)'
    try:
        wiki_images_dir = BaseFileNode.objects.get(_id=dir_id)
    except:
        logger.info('no wiki images')
    try:
        imported_wiki_workspace_folder = wiki_images_dir._children.get(name=imported_wiki_workspace_folder_name, type='osf.osfstoragefolder', deleted__isnull=True)
        path = '/' + imported_wiki_workspace_folder._id + '/'
        exist = True
    except:
        path = '/' + dir_id +'/'
        exist = False

    logger.info(path)
    logger.info(exist)

    return {'path': path, 'exist': exist}
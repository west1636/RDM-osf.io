# coding:utf-8
"""Views for the node settings page."""
from flask import request
from website import settings
import requests
import logging
import json
from osf.models import OSFUser
from website.project.views.node import node_contributors
from website.project.decorators import (
    must_be_contributor_or_public,
    must_have_addon,
    must_be_valid_project,
    must_not_be_retracted_registration,
)
from .translations.xattr import translate


# Get an instance of a logger
logger = logging.getLogger(__name__)

@must_be_valid_project
@must_be_contributor_or_public
@must_have_addon('xattr', 'node')
@must_not_be_retracted_registration
def xattr_widget(auth, wname, path=None, **kwargs):
    # What is this used for?
    ret = {
        'wiki_id': 'test id ',
        'wiki_name': 'testName',
    }
    return ret

@must_be_valid_project
@must_be_contributor_or_public
@must_have_addon('xattr', 'node')
@must_not_be_retracted_registration
def get_attributes(auth, path=None, **kwargs):
    context = node_contributors(**kwargs)
    user = OSFUser.objects.get(guids___id=context['user']['id'])
    language = user.locale[:2]
    language = 'ja'
    pid = kwargs['pid']

    context['dropdown_list'] = {
        'proj_affiliation': api_commonmaster_get('mng_dep', 'name', language),
        'proj_identifier': api_commonmaster_get('proj', 'name', language),
        'research_field': api_commonmaster_get('res_field', 'name', language),
        'range_type': api_commonmaster_get('range_type', 'name', language),
        'range': api_commonmaster_get('range', 'name', language),
        'funder_identifier': api_commonmaster_get('funder', 'name', language),
        'budget_category': api_commonmaster_get('budget_cat', 'name', language),
        'contributor_type': api_commonmaster_get('cont_type', 'name', language),
        'contributor_repr': api_commonmaster_get('cont_repr', 'name', language),
        'org_type': api_commonmaster_get('org_type', 'name', language),
        'ipd_identifier': api_commonmaster_get('ipd', 'name', language),
        'research_org': api_commonmaster_get('res_org', 'name', language),
        'org_recognition': api_commonmaster_get('org_recog', 'name', language),
        'storage_org': api_commonmaster_get('storage_org', 'name', language),
    }
    context['t'] = translate(['en', 'ja'])

    # Default content
    content = {
        'en': {
            'title': '',
            'organizationUnit': '',
            'projectIdentification': '',
            'researchField': '',
            'rangeType': [],
            'range': [],
            'startDate': '',
            'endDate': '',
            'description': '',
            'status': '1'
        },
        'ja': {
            'title': '',
            'organizationUnit': '',
            'projectIdentification': '',
            'researchField': '',
            'rangeType': [],
            'range': [],
            'startDate': '',
            'endDate': '',
            'description': '',
            'status': '1'
        }
    }
    try:
        content.update(json.loads(api_project_get(pid).text)['data'])
    except Exception:
        pass

    fundings = api_funding_get(pid)
    if fundings.status_code == 200:
        fundings = json.loads(fundings.text)['data']
    else:
        fundings = None
    content['fundings'] = json.dumps(fundings)

    contributors = api_contributor_get(pid)
    if contributors.status_code == 200:
        contributors = json.loads(contributors.text)['data']
    else:
        contributors = None
    content['contributors'] = json.dumps(contributors)

    context['content'] = content
    return context


@must_be_valid_project
@must_be_contributor_or_public
@must_have_addon('xattr', 'node')
@must_not_be_retracted_registration
def api_post_attributes(auth, path=None, **kwargs):
    pid = kwargs.get('pid')
    data = request.get_json()
    project_attribute = {
        'content': data['projectAttribute'],
        'user_id': auth.user.id,
        'status_id': int(data['projectAttribute']['en']['status'])
    }
    r1 = api_project_put(pid, project_attribute)

    funding_attribute = {
        'content': data['fundingAttribute'],
        'user_id': auth.user.id
    }
    r2 = api_funding_put(pid, funding_attribute)

    contributor_attribute = {
        'content': data['contributorAttribute'],
        'user_id': auth.user.id
    }
    r3 = api_contributor_put(pid, contributor_attribute)

    response = {
        'Status': 'OK'
    }
    if r1.status_code != 200 or r2.status_code != 200 or r3.status_code != 200:
        response['Status'] = 'Failed'
    else:
        # Register action to Activity Log
        node = kwargs['node']
        node.add_log(
            action='xattr_settings_edited',
            params={
                'node': pid,
                'project': pid
            },
            auth=auth
        )
    return response


def api_project_get(pid):
    url = '%sv2/attributes/project?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.get(url)


def api_project_put(pid, data):
    url = '%sv2/attributes/project?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.put(url, json=data)


def api_funding_get(pid):
    url = '%sv2/attributes/funding?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.get(url)


def api_funding_put(pid, data):
    url = '%sv2/attributes/funding?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.put(url, json=data)


def api_contributor_get(pid):
    url = '%sv2/attributes/contributor?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.get(url)


def api_contributor_put(pid, data):
    url = '%sv2/attributes/contributor?pid=%s' % (
        settings.XATTR_API_SERVER_URL,
        pid
    )
    return requests.put(url, json=data)


def api_commonmaster_get(table_type, field_name, language):
    url = '%sapi/commonmasters?table_type=%s&field_name=%s&lang=%s' % (
        settings.COMMONMASTER_API_SERVER_URL,
        table_type,
        field_name,
        language
    )
    resp = requests.get(url)
    return json.loads(resp.text)

# -*- coding: utf-8 -*-
"""
Timestamp views.
"""
from flask import request
from website.util import rubeus
from website.project.decorators import must_be_contributor_or_public
from website.project.views.node import _view_project
from website import settings
from osf.models import Guid, BaseFileNode
from website.util.timestamp import AddTimestamp
from website.util import timestamp
import requests
import os
import shutil
import logging


logger = logging.getLogger(__name__)

@must_be_contributor_or_public
def get_init_timestamp_error_data_list(auth, node, **kwargs):
    """
     get timestamp error data list (OSF view)
    """

    ctx = _view_project(node, auth, primary=True)
    ctx.update(rubeus.collect_addon_assets(node))
    pid = kwargs.get('pid')
    ctx['provider_list'] = timestamp.get_error_list(pid)
    ctx['project_title'] = node.title
    ctx['guid'] = pid
    ctx['web_api_url'] = settings.DOMAIN + node.api_url
    return ctx

@must_be_contributor_or_public
def get_timestamp_error_data(auth, node, **kwargs):
    # timestamp error data to timestamp or admin view
    if request.method == 'POST':
        request_data = request.json
        data = {}
        for key in request_data.keys():
            data.update({key: request_data[key][0]})
    else:
        data = request.args.to_dict()

    return timestamp.check_file_timestamp(auth.user.id, node, data)

@must_be_contributor_or_public
def add_timestamp_token(auth, node, **kwargs):
    # timestamptoken add method
    # request Get or Post data set
    if request.method == 'POST':
        request_data = request.json
        data = {}
        for key in request_data.keys():
            data.update({key: request_data[key][0]})

    else:
        data = request.args.to_dict()

    cookies = {settings.COOKIE_NAME: auth.user.get_or_create_cookie()}
    headers = {'content-type': 'application/json'}
    url = None
    tmp_dir = None
    try:
        file_node = BaseFileNode.objects.get(_id=data['file_id'])
        if data['provider'] == 'osfstorage':
            url = file_node.generate_waterbutler_url(
                **dict(
                    action='download',
                    version=data['version'],
                    direct=None, _internal=False
                )
            )

        else:
            url = file_node.generate_waterbutler_url(
                **dict(
                    action='download',
                    direct=None, _internal=False
                )
            )

        # Request To Download File
        res = requests.get(url, headers=headers, cookies=cookies)
        tmp_dir = 'tmp_{}'.format(auth.user._id)
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        download_file_path = os.path.join(tmp_dir, data['file_name'])
        with open(download_file_path, 'wb') as fout:
            fout.write(res.content)
            res.close()

        addTimestamp = AddTimestamp()
        result = addTimestamp.add_timestamp(
            auth.user._id, data['file_id'],
            node._id, data['provider'], data['file_path'],
            download_file_path, tmp_dir
        )

        shutil.rmtree(tmp_dir)
        return result

    except Exception as err:
        if tmp_dir:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)
        logger.exception(err)

@must_be_contributor_or_public
def collect_timestamp_trees_to_json(auth, node, **kwargs):
    # admin call project to provider file list
    serialized = _view_project(node, auth, primary=True)
    serialized.update(rubeus.collect_addon_assets(node))
    uid = Guid.objects.get(_id=serialized['user']['id']).object_id
    pid = kwargs.get('pid')

    return {'provider_list': timestamp.get_full_list(uid, pid, node)}

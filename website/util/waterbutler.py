# -*- coding: utf-8 -*-

import requests
import shutil
import os
from website import settings


def download_file(osf_cookie, file_node, download_path, **kwargs):
    '''
    Download an waterbutler file by streaming its contents while saving,
    so we do not waste memory.
    '''
    download_filename = file_node.name
    if not download_filename:
        download_filename = os.path.basename(file_node.path)
    assert download_filename

    full_path = os.path.join(download_path, download_filename)
    response = requests.get(
        file_node.generate_waterbutler_url(action='download', direct=None, **kwargs),
        cookies={settings.COOKIE_NAME: osf_cookie},
        stream=True
    )

    with open(full_path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    response.close()
    return full_path

# -*- coding: utf-8 -*-
#
# @COPYRIGHT@
#

import logging
import os
import sys

from framework.celery_tasks import app as celery_app

# global setting
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logger.setLevel(level=logging.DEBUG)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'api.base.settings'
    from website.app import init_app
    init_app(routes=False, set_backends=False)

from osf.models.user import OSFUser
from nii.mapcore_api import MAPCore

def mapcore_refresh_tokens(debug=False):
    for user in OSFUser.objects.all():
        if user.map_profile is not None:
            if user.map_profile.oauth_access_token is not None:
                if debug:
                    logger.info('Refreshing: ' + user.username + ' (' + user.map_profile.oauth_access_token + ')')

                mapcore_api = MAPCore(user)
                mapcore_api.refresh_token()

@celery_app.task(name='nii.mapcore_refresh_tokens')
def run_main(rate_limit=(5, 1), dry_run=True):
    if not dry_run:
        mapcore_refresh_tokens()
    pass

# for test
if __name__ == '__main__':
    # Get existent OSFUsers.
    mapcore_refresh_tokens(True)

    logger.info('Function completed')
    sys.exit()

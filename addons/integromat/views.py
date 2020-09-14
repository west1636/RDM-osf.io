# -*- coding: utf-8 -*-
from flask import request
import logging


from addons.base import generic_views
from framework.auth.decorators import must_be_logged_in
from addons.integromat.serializer import IntegromatSerializer
#from addons.integromat.apps import IntegromatSerializer
from osf.models import ExternalAccount
from django.core.exceptions import ValidationError
from framework.exceptions import HTTPError
from rest_framework import status as http_status

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
def integromat_add_user_account(auth, **kwargs):
    """Verifies new external account credentials and adds to user's list"""

    logger.info('xxx:' + str(auth))
    logger.info('xxx::' + str(kwargs))

    try:
        access_token = request.json.get('integromat_api_token')
        logger.info('yyy:' + str(access_token))
    except KeyError:
        raise HTTPError(http_status.HTTP_400_BAD_REQUEST)

    #integromat認証レクエスト投げる#

    try:
        account = ExternalAccount(
            provider=SHORT_NAME,
            provider_name=FULL_NAME,
            display_name='TESTUSER',
#            display_name=user.username,
            oauth_key=access_token,
            provider_id=access_token,
        )
        account.save()
    except ValidationError:
        # ... or get the old one
        account = ExternalAccount.objects.get(
            provider='integromat', provider_id=access_token
        )
        if account.oauth_key != access_token:
            account.oauth_key = access_token
            account.save()

    user = auth.user
    logger.info('zzz:' + str(auth))
    logger.info('zzz:' + str(user))
    logger.info('zzz:' + str(account.id))
#    logger.info('zzz:' + str(user.external_accounts.values()))

    if not user.external_accounts.filter(id=account.id).exists():
        logger.info('nnn')
        user.external_accounts.add(account)

    user.get_or_add_addon('integromat', auth=auth)

    user.save()

    logger.info('zzz3:' + str(user.get_addon('integromat').has_auth))

    return {}

integromat_deauthorize_node = generic_views.deauthorize_node(
    SHORT_NAME
)

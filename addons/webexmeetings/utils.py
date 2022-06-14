# -*- coding: utf-8 -*-
import json
import requests
from osf.models import ExternalAccount
from addons.webexmeetings import models
from addons.webexmeetings import settings
from django.core import serializers
import logging
from datetime import timedelta
import dateutil.parser
from django.db import transaction
logger = logging.getLogger(__name__)

# widget: ここから
def serialize_webexmeetings_widget(node):
    webexmeetings = node.get_addon('webexmeetings')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': webexmeetings.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(webexmeetings.config.to_json())
    return ret
# widget: ここまで

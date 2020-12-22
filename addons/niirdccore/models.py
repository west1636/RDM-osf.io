# -*- coding: utf-8 -*-
import logging
import json

from django.db import models
from osf.models.node import Node

from . import settings
from addons.base.models import BaseNodeSettings
from website import settings as ws_settings

logger = logging.getLogger(__name__)

class NodeSettings(BaseNodeSettings):
    """
    プロジェクトにアタッチされたアドオンに関するモデルを定義する。
    """

    def get_dmr_api_key(self):
        return settings.DMR_API_KEY

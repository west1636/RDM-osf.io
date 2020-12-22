# -*- coding: utf-8 -*-
"""
本アドオンの各種プロパティを定義する
"""

import os
from addons.base.apps import BaseAddonAppConfig
from . import SHORT_NAME

# `__init__.py` の `default_app_config` により本ファイル内の`AddonAppConfig`が参照される
class AddonAppConfig(BaseAddonAppConfig):

    short_name = SHORT_NAME
    name = 'addons.{}'.format(SHORT_NAME)
    label = 'addons_{}'.format(SHORT_NAME)

    full_name = 'NII RDC Core'

    owners = ['node']

    views = []
    configs = ['node']

    categories = ['other']

    include_js = {}

    include_css = {}

    @property
    def routes(self):
        from . import routes
        return [routes.api_routes]

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')

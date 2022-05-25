# -*- coding: utf-8 -*-
"""Routes for the zoommeetings addon.
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate

from addons.zoommeetings import views

TEMPLATE_DIR = './addons/zoommeetings/templates/'

# HTML endpoints
page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/<pid>/zoommeetings',
                '/<pid>/node/<nid>/zoommeetings',
            ],
            'get',
            views.project_zoommeetings,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/settings/zoommeetings/accounts/',
            'post',
            views.zoommeetings_add_user_account,
            json_renderer,
        ),

        Rule(
            [
                '/settings/zoommeetings/accounts/',
            ],
            'get',
            views.zoommeetings_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/zoommeetings/settings/',
                '/project/<pid>/node/<nid>/zoommeetings/settings/'
            ],
            'get',
            views.zoommeetings_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/zoommeetings/user_auth/',
                '/project/<pid>/node/<nid>/zoommeetings/user_auth/'
            ],
            'put',
            views.zoommeetings_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/zoommeetings/user_auth/',
                '/project/<pid>/node/<nid>/zoommeetings/user_auth/'
            ],
            'delete',
            views.zoommeetings_deauthorize_node,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/zoommeetings/get_meetings',
                '/project/<pid>/node/<nid>/zoommeetings/get_meetings',
            ],
            'get',
            views.zoommeetings_get_meetings,
            json_renderer,
        ),

        # ember: ここから
        Rule([
            '/project/<pid>/zoommeetings/config',
            '/project/<pid>/node/<nid>/zoommeetings/config',
        ], 'get', views.zoommeetings_get_config_ember, json_renderer),
        Rule([
            '/project/<pid>/zoommeetings/config',
            '/project/<pid>/node/<nid>/zoommeetings/config',
        ], 'patch', views.zoommeetings_set_config_ember, json_renderer),
        # ember: ここまで

    ],
    'prefix': '/api/v1'
}

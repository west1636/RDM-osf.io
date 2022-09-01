# -*- coding: utf-8 -*-
"""Routes for the webexmeetings addon.
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate

from addons.webexmeetings import views

TEMPLATE_DIR = './addons/webexmeetings/templates/'

# HTML endpoints
page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/<pid>/webexmeetings',
                '/<pid>/node/<nid>/webexmeetings',
            ],
            'get',
            views.project_webexmeetings,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/oauth/connect/webexmeetings',
            'post',
            views.webexmeetings_oauth_connect,
            json_renderer,
        ),

        Rule(
            [
                '/settings/webexmeetings/accounts/',
            ],
            'get',
            views.webexmeetings_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/webexmeetings/settings/',
                '/project/<pid>/node/<nid>/webexmeetings/settings/'
            ],
            'get',
            views.webexmeetings_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/webexmeetings/user_auth/',
                '/project/<pid>/node/<nid>/webexmeetings/user_auth/'
            ],
            'put',
            views.webexmeetings_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/webexmeetings/user_auth/',
                '/project/<pid>/node/<nid>/webexmeetings/user_auth/'
            ],
            'delete',
            views.webexmeetings_deauthorize_node,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/webexmeetings/request_api',
                '/project/<pid>/node/<nid>/webexmeetings/request_api',
            ],
            'post',
            views.webexmeetings_request_api,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/webexmeetings/register_email',
                '/project/<pid>/node/<nid>/webexmeetings/register_email',
            ],
            'post',
            views.webexmeetings_register_email,
            json_renderer,
        ),

        # ember: ここから
        Rule([
            '/project/<pid>/webexmeetings/config',
            '/project/<pid>/node/<nid>/webexmeetings/config',
        ], 'get', views.webexmeetings_get_config_ember, json_renderer),
        Rule([
            '/project/<pid>/webexmeetings/config',
            '/project/<pid>/node/<nid>/webexmeetings/config',
        ], 'patch', views.webexmeetings_set_config_ember, json_renderer),
        # ember: ここまで

    ],
    'prefix': '/api/v1'
}

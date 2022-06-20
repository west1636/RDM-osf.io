# -*- coding: utf-8 -*-
"""Routes for the microsoftteams addon.
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate

from addons.microsoftteams import views

TEMPLATE_DIR = './addons/microsoftteams/templates/'

# HTML endpoints
page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/<pid>/microsoftteams',
                '/<pid>/node/<nid>/microsoftteams',
            ],
            'get',
            views.project_microsoftteams,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/oauth/connect/microsoftteams',
            'post',
            views.microsoftteams_oauth_connect,
            json_renderer,
        ),

        Rule(
            [
                '/settings/microsoftteams/accounts/',
            ],
            'get',
            views.microsoftteams_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/microsoftteams/settings/',
                '/project/<pid>/node/<nid>/microsoftteams/settings/'
            ],
            'get',
            views.microsoftteams_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/microsoftteams/user_auth/',
                '/project/<pid>/node/<nid>/microsoftteams/user_auth/'
            ],
            'put',
            views.microsoftteams_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/microsoftteams/user_auth/',
                '/project/<pid>/node/<nid>/microsoftteams/user_auth/'
            ],
            'delete',
            views.microsoftteams_deauthorize_node,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/microsoftteams/request_api',
                '/project/<pid>/node/<nid>/microsoftteams/request_api',
            ],
            'post',
            views.microsoftteams_request_api,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/microsoftteams/get_meetings',
                '/project/<pid>/node/<nid>/microsoftteams/get_meetings',
            ],
            'get',
            views.microsoftteams_get_meetings,
            json_renderer,
        ),

        # ember: ここから
        Rule([
            '/project/<pid>/microsoftteams/config',
            '/project/<pid>/node/<nid>/microsoftteams/config',
        ], 'get', views.microsoftteams_get_config_ember, json_renderer),
        Rule([
            '/project/<pid>/microsoftteams/config',
            '/project/<pid>/node/<nid>/microsoftteams/config',
        ], 'patch', views.microsoftteams_set_config_ember, json_renderer),
        # ember: ここまで

    ],
    'prefix': '/api/v1'
}

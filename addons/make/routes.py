# -*- coding: utf-8 -*-
"""Routes for the make addon.
"""

from framework.routing import Rule, json_renderer
from website.routes import notemplate

from addons.make import views

TEMPLATE_DIR = './addons/make/templates/'

# HTML endpoints
page_routes = {

    'rules': [

        # Home (Base) | GET
        Rule(
            [
                '/<pid>/grdmapps',
                '/<pid>/node/<nid>/grdmapps',
            ],
            'get',
            views.project_grdmapps,
            notemplate
        ),

    ]
}

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/settings/make/accounts/',
            'post',
            views.make_add_user_account,
            json_renderer,
        ),

        Rule(
            [
                '/settings/make/accounts/',
            ],
            'get',
            views.make_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/make/settings/',
                '/project/<pid>/node/<nid>/make/settings/'
            ],
            'get',
            views.make_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/make/user_auth/',
                '/project/<pid>/node/<nid>/make/user_auth/'
            ],
            'put',
            views.make_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/make/user_auth/',
                '/project/<pid>/node/<nid>/make/user_auth/'
            ],
            'delete',
            views.make_deauthorize_node,
            json_renderer,
        ),
        #route for Integromat action
        Rule(
            '/integromat/integromat_api_call',
            'get',
            views.make_api_call,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/get_file_id',
                '/project/<pid>/node/<nid>/integromat/get_file_id',
            ],
            'post',
            views.make_get_file_id,
            json_renderer,
        ),

        Rule(
            '/integromat/get_node',
            'post',
            views.make_get_node,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/link_to_node',
                '/project/<pid>/node/<nid>/integromat/link_to_node',
            ],
            'post',
            views.make_link_to_node,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/watch_comment',
                '/project/<pid>/node/<nid>/integromat/watch_comment',
            ],
            'post',
            views.make_watch_comment,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/start_scenario',
                '/project/<pid>/node/<nid>/integromat/start_scenario',
            ],
            'post',
            views.make_start_scenario,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/requestNextMessages',
                '/project/<pid>/node/<nid>/integromat/requestNextMessages',
            ],
            'post',
            views.make_req_next_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/register_alternative_webhook_url',
                '/project/<pid>/node/<nid>/integromat/register_alternative_webhook_url',
            ],
            'post',
            views.make_register_alternative_webhook_url,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/register_web_meeting_apps_email',
                '/project/<pid>/node/<nid>/integromat/register_web_meeting_apps_email',
            ],
            'post',
            views.make_register_web_meeting_apps_email,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/info_msg',
                '/project/<pid>/node/<nid>/integromat/info_msg',
            ],
            'post',
            views.make_info_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/error_msg',
                '/project/<pid>/node/<nid>/integromat/error_msg',
            ],
            'post',
            views.make_error_msg,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/get_meetings',
                '/project/<pid>/node/<nid>/integromat/get_meetings',
            ],
            'get',
            views.make_get_meetings,
            json_renderer,
        ),

        # ember: ここから
        Rule([
            '/project/<pid>/grdmapps/config',
            '/project/<pid>/node/<nid>/grdmapps/config',
        ], 'get', views.grdmapps_get_config_ember, json_renderer),
        Rule([
            '/project/<pid>/grdmapps/config',
            '/project/<pid>/node/<nid>/grdmapps/config',
        ], 'patch', views.grdmapps_set_config_ember, json_renderer),
        # ember: ここまで

    ],
    'prefix': '/api/v1'
}

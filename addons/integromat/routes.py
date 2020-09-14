# -*- coding: utf-8 -*-
"""Routes for the integromat addon.
"""

from framework.routing import Rule, json_renderer

from addons.integromat import views

# JSON endpoints
api_routes = {
    'rules': [

        Rule(
            '/settings/integromat/accounts/',
            'post',
            views.integromat_add_user_account,
            json_renderer,
        ),

        Rule(
            [
                '/settings/integromat/accounts/',
            ],
            'get',
            views.integromat_account_list,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/settings/integromat/',
                '/project/<pid>/node/<nid>/settings/integromat/'
            ],
            'get',
            views.integromat_get_config,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/user_auth/',
                '/project/<pid>/node/<nid>/integromat/user_auth/'
            ],
            'put',
            views.integromat_import_auth,
            json_renderer,
        ),

        Rule(
            [
                '/project/<pid>/integromat/user_auth/',
                '/project/<pid>/node/<nid>/integromat/user_auth/'
            ],
            'delete',
            views.integromat_deauthorize_node,
            json_renderer,
        ),

    ],
    'prefix': '/api/v1'
}

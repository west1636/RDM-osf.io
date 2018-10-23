"""
Routes associated with the xattr page
"""

from framework.routing import Rule, json_renderer
from website.routes import OsfWebRenderer
from . import views


TEMPLATE_DIR = './addons/xattr/templates/'

widget_routes = {
    'rules': [
        Rule(
            [
                '/project/<pid>/xattr/widget/',
            ],
            'get',
            views.xattr_widget,
            json_renderer
        ),
    ],
    'prefix': '/api/v1',
}

page_routes = {
    'rules': [
        Rule(
            [
                '/project/<pid>/xattr/',
            ],
            'get',
            views.get_attributes,
            OsfWebRenderer('xattr.mako', trust=False, template_dir=TEMPLATE_DIR)
        ),
    ]
}

api_routes = {
    'rules': [
        Rule(
            [
                '/project/<pid>/xattr/',
            ],
            'post',
            views.api_post_attributes,
            json_renderer
        ),
    ],
    'prefix': '/api/v1',
}

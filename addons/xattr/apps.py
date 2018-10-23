from addons.base.apps import BaseAddonAppConfig


class XattrAddonAppConfig(BaseAddonAppConfig):

    name = 'addons.xattr'
    label = 'addons_xattr'
    short_name = 'xattr'
    full_name = 'Attributes'
    owners = ['node']
    added_default = ['node']
    added_mandatory = []
    views = ['widget', 'page']
    configs = []
    categories = ['documentation']

    include_js = {
        'widget': [],
        'page': [],
    }

    include_css = {
        'widget': [],
        'page': [],
    }

    @property
    def routes(self):
        from addons.xattr import routes
        return [routes.widget_routes, routes.page_routes, routes.api_routes]

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')

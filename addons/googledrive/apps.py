import os

from addons.base.apps import BaseAddonAppConfig, generic_root_folder
from addons.googledrive.settings import MAX_UPLOAD_SIZE

googledrive_root_folder = generic_root_folder('googledrive')

HERE = os.path.dirname(os.path.abspath(__file__))
NODE_SETTINGS_TEMPLATE = os.path.join(HERE, 'templates', 'googledrive_node_settings.mako')
USER_SETTINGS_TEMPLATE = os.path.join(HERE, 'templates', 'googledrive_user_settings.mako')

class GoogleDriveAddonConfig(BaseAddonAppConfig):

    name = 'addons.googledrive'
    label = 'addons_googledrive'
    full_name = 'Google Drive'
    short_name = 'googledrive'
    owners = ['user', 'node']
    configs = ['accounts', 'node']
    categories = ['storage']
    has_hgrid_files = True
    max_file_size = MAX_UPLOAD_SIZE
    node_settings_template = NODE_SETTINGS_TEMPLATE
    user_settings_template = USER_SETTINGS_TEMPLATE

    @property
    def get_hgrid_data(self):
        return googledrive_root_folder

    FOLDER_SELECTED = 'googledrive_folder_selected'
    NODE_AUTHORIZED = 'googledrive_node_authorized'
    NODE_DEAUTHORIZED = 'googledrive_node_deauthorized'

    actions = (FOLDER_SELECTED, NODE_AUTHORIZED, NODE_DEAUTHORIZED, )

    @property
    def routes(self):
        from . import routes
        return [routes.api_routes]

    @property
    def user_settings(self):
        return self.get_model('UserSettings')

    @property
    def node_settings(self):
        return self.get_model('NodeSettings')

from addons.base.serializer import OAuthAddonSerializer
import logging

logger = logging.getLogger(__name__)


class IntegromatSerializer(OAuthAddonSerializer):
    addon_short_name = 'integromat'

    @property
    def addon_serialized_urls(self):
        node = self.node_settings.owner
        user = self.user_settings

        result = {
            'create': node.api_url_for('integromat_add_user_account', user_settings=user),
            'deauthorize': node.api_url_for('integromat_deauthorize_node'),
        }

        return result

    def serialize_settings(self, node_settings, user):

        if not self.node_settings:
            self.node_settings = node_settings
        if not self.user_settings:
            self.user_settings = user.get_addon(self.addon_short_name)

        result = {
            'urls': self.addon_serialized_urls,
        }
        return result

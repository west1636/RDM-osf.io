from addons.base.serializer import OAuthAddonSerializer
import logging

logger = logging.getLogger(__name__)


class IntegromatSerializer(OAuthAddonSerializer):
    addon_short_name = 'integromat'

    REQUIRED_URLS = []
    
    def grant_oauth_access(self, node, user, external_account, metadata=None):
        """Give a node permission to use an ``ExternalAccount`` instance."""
#        # ensure the user owns the external_account
#        if not self.node_settings.external_account.filter(id=external_account.id).exists():
#            raise PermissionsError()

        metadata = metadata or {}

        # create an entry for the node, if necessary
        if node._id not in self.oauth_grants:
            self.oauth_grants[node._id] = {}

        # create an entry for the external account on the node, if necessary
        if external_account._id not in user.oauth_grants[node._id]:
            user.oauth_grants[node._id][external_account._id] = {}

        # update the metadata with the supplied values
        for key, value in metadata.items():
            self.oauth_grants[node._id][external_account._id][key] = value

        self.save()

    @property
    def serialized_urls(self):

        ret = self.addon_serialized_urls

        return ret

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
            'urls': self.serialized_urls,
        }
        return result

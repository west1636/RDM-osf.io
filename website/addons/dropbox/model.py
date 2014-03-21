# -*- coding: utf-8 -*-
from modularodm import Q
from modularodm.exceptions import ModularOdmException

from framework import fields
from website.addons.base import AddonUserSettingsBase, AddonNodeSettingsBase, GuidFile

from website.addons.dropbox.client import get_client

class DropboxFile(GuidFile):

    #: Full path to the file, e.g. 'My Pictures/foo.png'
    path = fields.StringField(required=True, index=True)

    @property
    def api_url(self):
        """The api url for the file."""
        return self.node.api_url_for('dropbox_view_file', path=self.path)

    @property
    def url(self):
        """The web url for the file."""
        return self.node.web_url_for('dropbox_view_file', path=self.path)

    @classmethod
    def get_or_create(cls, node, path):
        """Get or create a new file record.
        Return a tuple of the form ``obj, created``
        """
        try:
            new = cls.find_one(
                Q('node', 'eq', node),
                Q('path', 'eq', path)
            )
            created = False
        except ModularOdmException:
            # Create new
            new = cls(node=node, path=path)
            new.save()
            created = True
        return new, created


class DropboxUserSettings(AddonUserSettingsBase):
    """Stores user-specific dropbox information, including the Oauth access
    token.
    """

    dropbox_id = fields.StringField(required=False)
    access_token = fields.StringField(required=False)
    account_info = fields.DictionaryField(required=False)

    # TODO(sloria): The `user` param in unnecessary for AddonUserSettings
    def to_json(self, user=None):
        """Return a dictionary representation of the user settings.
        The dictionary keys and values will be available as variables in
        dropbox_user_settings.mako.
        """
        output = super(DropboxUserSettings, self).to_json(self.owner)
        output['has_auth'] = self.has_auth
        return output

    @property
    def has_auth(self):
        return bool(self.access_token)

    def update_account_info(self, client=None):
        """Update Dropbox account info by fetching data from the Dropbox API.
        """
        c = client or get_client(self.owner)
        self.account_info = c.account_info()

    def get_account_info(self, client=None, force=False):
        """Gets the account info from the Dropbox API (cached).
        """
        if force or (not self.account_info):
            self.update_account_info(client=client)
            return self.account_info
        return self.account_info

    def clear_auth(self):
        self.dropbox_id = None
        self.access_token = None
        return self

    def delete(self):
        super(DropboxUserSettings, self).delete()
        self.clear_auth()
        for node_settings in self.dropboxnodesettings__authorized:
            node_settings.delete(save=False)
            node_settings.user_settings = None
            node_settings.save()


class DropboxNodeSettings(AddonNodeSettingsBase):

    user_settings = fields.ForeignField(
        'dropboxusersettings', backref='authorized'
    )

    folder = fields.StringField(default='')

    @property
    def has_auth(self):
        return self.user_settings and self.user_settings.has_auth

    def delete(self, save=True):
        super(DropboxNodeSettings, self).delete(save=False)
        if save:
            self.save()

    # TODO
    def to_json(self, user):
        ret = super(DropboxNodeSettings, self).to_json(user)
        if not self.user_settings:
            self.folder = '/'
            self.user_settings = user.get_addon('dropbox')
            self.save()
        ret.update({
            'folder': self.folder or '',
            'node_has_auth': self.has_auth,
            'is_owner': False,
            'user_has_auth': self.user_settings.owner == user,
            #  TODO
            # 'owner_url': '',
            'owner_info': self.user_settings.account_info,
        })

        return ret

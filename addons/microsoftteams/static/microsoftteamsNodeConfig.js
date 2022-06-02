'use strict';

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var osfHelpers = require('js/osfHelpers');
var oop = require('js/oop');
var m = require('mithril');
var bootbox = require('bootbox');
var $osf = require('js/osfHelpers');
var OauthAddonFolderPicker = require('js/oauthAddonNodeConfig')._OauthAddonNodeConfigViewModel;
var _ = require('js/rdmGettext')._;
var sprintf = require('agh.sprintf').sprintf;

var MicrosoftTeamsFolderPickerViewModel = oop.extend(OauthAddonFolderPicker, {
    constructor: function(addonName, url, selector, folderPicker, opts, tbOpts) {
        var self = this;
        // TODO: [OSF-7069]
        self.super.super.constructor.call(self, addonName, url, selector, folderPicker, tbOpts);
        self.super.construct.call(self, addonName, url, selector, folderPicker, opts, tbOpts);

        // Non-OAuth fields
        self.microsoftteamsTenant = ko.observable();
        self.microsoftteamsClientId = ko.observable();
        self.microsoftteamsClientSecret = ko.observable();

    },

    connectAccount: function() {
        var self = this;
        if (!self.microsoftteamsTenant() ){
            self.changeMessage('Please enter a Microsoft 365 Tenant ID', 'text-danger');
            return;
        }
        if (!self.microsoftteamsClientId() ){
            self.changeMessage('Please enter an Application(Client) ID.', 'text-danger');
            return;
        }
        if (!self.microsoftteamsClientSecret() ){
            self.changeMessage('Please enter a Client Secret.', 'text-danger');
            return;
        }

        $osf.block();

        return $osf.postJSON(
            self.urls().create, {
                microsoftteams_tenant: self.microsoftteamsTenant(),
                microsoftteams_client_id: self.microsoftteamsClientId(),
                microsoftteams_client_secret: self.microsoftteamsClientSecret(),
            }
        ).done(function(response) {
            $osf.unblock();
            self.clearModal();
            $('#microsoftteamsCredentialsModal').modal('hide');
            self.changeMessage(_('Successfully added Microsoft 365 credentials.'), 'text-success', null, true);
            self.updateFromData(response);
            self.importAuth();
        }).fail(function(xhr, status, error) {
            $osf.unblock();
            var message = '';
            var response = JSON.parse(xhr.responseText);
            if (response && response.message) {
                message = response.message;
            }
            self.changeMessage(message, 'text-danger');
            Raven.captureMessage(_('Could not add Microsoft 365 credentials'), {
                extra: {
                    url: self.urls().importAuth,
                    textStatus: status,
                    error: error
                }
            });
        });
    },

    /** Reset all fields from Microsoft 365 credentials input modal */
    clearModal: function() {
        var self = this;
        self.message('');
        self.messageClass('text-info');
        self.microsoftteamsTenant(null);
        self.microsoftteamsClientId(null);
        self.microsoftteamsClientSecret(null);
    },
});

// Public API
function MicrosoftTeamsNodeConfig(addonName, selector, url, folderPicker, opts, tbOpts) {
    var self = this;
    self.url = url;
    self.folderPicker = folderPicker;
    opts = opts || {};
    tbOpts = tbOpts || {};
    self.viewModel = new MicrosoftTeamsFolderPickerViewModel(addonName, url, selector, folderPicker, opts, tbOpts);
    self.viewModel.updateFromData();
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = {
    MicrosoftTeamsNodeConfig: MicrosoftTeamsNodeConfig,
    _MicrosoftTeamsNodeConfigViewModel: MicrosoftTeamsFolderPickerViewModel
};

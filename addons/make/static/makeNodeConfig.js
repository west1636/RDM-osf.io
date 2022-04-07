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

var MakeFolderPickerViewModel = oop.extend(OauthAddonFolderPicker, {
    constructor: function(addonName, url, selector, folderPicker, opts, tbOpts) {
        var self = this;
        // TODO: [OSF-7069]
        self.super.super.constructor.call(self, addonName, url, selector, folderPicker, tbOpts);
        self.super.construct.call(self, addonName, url, selector, folderPicker, opts, tbOpts);

        // Non-OAuth fields
        self.makeApiToken = ko.observable();
        self.userGuid = ko.observable();
        self.microsoftTeamsUserName = ko.observable();
        self.microsoftTeamsMail = ko.observable();
        self.webexMeetingsDisplayName = ko.observable();
        self.webexMeetingsMail = ko.observable();
        self.userGuidToDelete = ko.observable();

    },

    connectAccount: function() {
        var self = this;
        if (!self.makeApiToken() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }
        $osf.block();

        return $osf.postJSON(
            self.urls().create, {
                make_api_token: self.makeApiToken(),
            }
        ).done(function(response) {
            $osf.unblock();
            self.clearModal();
            $('#makeCredentialsModal').modal('hide');
            self.changeMessage(_('Successfully added Make credentials.'), 'text-success', null, true);
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
            Raven.captureMessage(_('Could not add Make credentials'), {
                extra: {
                    url: self.urls().importAuth,
                    textStatus: status,
                    error: error
                }
            });
        });
    },

    /** Reset all fields from Make credentials input modal */
    clearModal: function() {
        var self = this;
        self.message('');
        self.messageClass('text-info');
        self.makeApiToken(null);
    },
});

// Public API
function MakeNodeConfig(addonName, selector, url, folderPicker, opts, tbOpts) {
    var self = this;
    self.url = url;
    self.folderPicker = folderPicker;
    opts = opts || {};
    tbOpts = tbOpts || {};
    self.viewModel = new MakeFolderPickerViewModel(addonName, url, selector, folderPicker, opts, tbOpts);
    self.viewModel.updateFromData();
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = {
    MakeNodeConfig: MakeNodeConfig,
    _MakeNodeConfigViewModel: MakeFolderPickerViewModel
};

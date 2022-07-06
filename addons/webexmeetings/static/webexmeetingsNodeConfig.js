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

var WebexMeetingsFolderPickerViewModel = oop.extend(OauthAddonFolderPicker, {
    constructor: function(addonName, url, selector, folderPicker, opts, tbOpts) {
        var self = this;
        // TODO: [OSF-7069]
        self.super.super.constructor.call(self, addonName, url, selector, folderPicker, tbOpts);
        self.super.construct.call(self, addonName, url, selector, folderPicker, opts, tbOpts);

        // Non-OAuth fields
        self.webexmeetingsClientId = ko.observable();
        self.webexmeetingsClientSecret = ko.observable();
        self.webexmeetingsOAuthUrl = ko.observable();

    },

    connectAccount: function() {
        var self = this;
        if (!self.webexmeetingsClientId() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }
        if (!self.webexmeetingsClientSecret() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }
        if (!self.webexmeetingsOAuthUrl() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }

        $osf.block();

        return $osf.postJSON(
            self.urls().auth, {
                webexmeetings_client_id: self.webexmeetingsClientId(),
                webexmeetings_client_secret: self.webexmeetingsClientSecret(),
                webexmeetings_oauth_url: self.webexmeetingsOAuthUrl(),
            }
        ).done(function(response) {
            $osf.unblock();
            self.clearModal();
            $('#webexmeetingsCredentialsModal').modal('hide');
            self.changeMessage(_('Successfully added Webex Meetings credentials.'), 'text-success', null, true);
            window.oauthComplete = function(res) {
                // Update view model based on response
                self.updateAccounts().then(function() {
                    try{
                        $osf.putJSON(
                            self.urls().importAuth, {
                                external_account_id: self.accounts()[0].id
                            }
                        ).done(self.onImportSuccess.bind(self)
                        ).fail(self.onImportError.bind(self));

                        self.changeMessage(self.messages.connectAccountSuccess(), 'text-success', 3000);
                    }
                    catch(err){
                        self.changeMessage(self.messages.connectAccountDenied(), 'text-danger', 6000);
                    }
                });
            };
            window.open(response);
        }).fail(function(xhr, status, error) {
            $osf.unblock();
            var message = '';
            var response = JSON.parse(xhr.responseText);
            if (response && response.message) {
                message = response.message;
            }
            self.changeMessage(message, 'text-danger');
            Raven.captureMessage(_('Could not add Zoom Meetings credentials'), {
                extra: {
                    url: self.urls().importAuth,
                    textStatus: status,
                    error: error
                }
            });
        });

    },

    /** Reset all fields from Webex Meetings credentials input modal */
    clearModal: function() {
        var self = this;
        self.message('');
        self.messageClass('text-info');
        self.webexmeetingsClientId(null);
        self.webexmeetingsClientSecret(null);
        self.webexmeetingsOAuthUrl(null);
    },
});

// Public API
function WebexMeetingsNodeConfig(addonName, selector, url, folderPicker, opts, tbOpts) {
    var self = this;
    self.url = url;
    self.folderPicker = folderPicker;
    opts = opts || {};
    tbOpts = tbOpts || {};
    self.viewModel = new WebexMeetingsFolderPickerViewModel(addonName, url, selector, folderPicker, opts, tbOpts);
    self.viewModel.updateFromData();
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = {
    WebexMeetingsNodeConfig: WebexMeetingsNodeConfig,
    _WebexMeetingsNodeConfigViewModel: WebexMeetingsFolderPickerViewModel
};

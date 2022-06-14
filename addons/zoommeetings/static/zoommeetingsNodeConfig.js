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

var ZoomMeetingsFolderPickerViewModel = oop.extend(OauthAddonFolderPicker, {
    constructor: function(addonName, url, selector, folderPicker, opts, tbOpts) {
        var self = this;
        // TODO: [OSF-7069]
        self.super.super.constructor.call(self, addonName, url, selector, folderPicker, tbOpts);
        self.super.construct.call(self, addonName, url, selector, folderPicker, opts, tbOpts);

        // Non-OAuth fields
        self.zoommeetingsEmail = ko.observable();
        self.zoommeetingsJwtToken = ko.observable();

    },

    connectAccount: function() {
        var self = this;
        if (!self.zoommeetingsEmail() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }
        if (!self.zoommeetingsJwtToken() ){
            self.changeMessage(_('Please enter an API token.'), 'text-danger');
            return;
        }

        $osf.block();

        return $osf.postJSON(
            self.urls().create, {
                zoommeetings_email: self.zoommeetingsEmail(),
                zoommeetings_jwt_token: self.zoommeetingsJwtToken(),
            }
        ).done(function(response) {
            $osf.unblock();
            self.clearModal();
            $('#zoommeetingsCredentialsModal').modal('hide');
            self.changeMessage(_('Successfully added Zoom Meetings credentials.'), 'text-success', null, true);
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
            Raven.captureMessage(_('Could not add Zoom Meetings credentials'), {
                extra: {
                    url: self.urls().importAuth,
                    textStatus: status,
                    error: error
                }
            });
        });
    },

    /** Reset all fields from Zoom Meetings credentials input modal */
    clearModal: function() {
        var self = this;
        self.message('');
        self.messageClass('text-info');
        self.zoommeetingsEmail(null);
        self.zoommeetingsJwtToken(null);
    },
});

// Public API
function ZoomMeetingsNodeConfig(addonName, selector, url, folderPicker, opts, tbOpts) {
    var self = this;
    self.url = url;
    self.folderPicker = folderPicker;
    opts = opts || {};
    tbOpts = tbOpts || {};
    self.viewModel = new ZoomMeetingsFolderPickerViewModel(addonName, url, selector, folderPicker, opts, tbOpts);
    self.viewModel.updateFromData();
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = {
    ZoomMeetingsNodeConfig: ZoomMeetingsNodeConfig,
    _ZoomMeetingsNodeConfigViewModel: ZoomMeetingsFolderPickerViewModel
};

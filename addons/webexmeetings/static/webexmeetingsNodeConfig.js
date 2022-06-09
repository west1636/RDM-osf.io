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

        window.open(self.urls().auth);

        $osf.unblock();
        self.clearModal();
        $('#webexmeetingsCredentialsModal').modal('hide');

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

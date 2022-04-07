/**
* Module that controls the Make user settings. Includes Knockout view-model
* for syncing data.
*/

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');
require('js/osfToggleHeight');

var language = require('js/osfLanguage').Addons.make;
var osfHelpers = require('js/osfHelpers');
var addonSettings = require('js/addonSettings');
var ChangeMessageMixin = require('js/changeMessage');
var ExternalAccount = addonSettings.ExternalAccount;

var _ = require('js/rdmGettext')._;
var sprintf = require('agh.sprintf').sprintf;

var $modal = $('#makeCredentialsModal');

function ViewModel(url) {
    var self = this;

    self.properName = 'Make';
    self.accessKey = ko.observable();
    self.secretKey = ko.observable();
    self.account_url = '/api/v1/settings/make/accounts/';
    self.accounts = ko.observableArray();

    self.makeApiToken = ko.observable();

    self.userGuid = ko.observable();
    self.microsoftTeamsUserName = ko.observable();
    self.microsoftTeamsMail = ko.observable();
    self.webexMeetingsDisplayName = ko.observable();
    self.webexMeetingsMail = ko.observable();
    self.userGuidToDelete = ko.observable();

    ChangeMessageMixin.call(self);

    /** Reset all fields from Make credentials input modal */
    self.clearModal = function() {
        self.message('');
        self.messageClass('text-info');
        self.makeApiToken(null);
    };
    /** Send POST request to authorize Make */
    self.connectAccount = function() {
        // Selection should not be empty
        if (!self.makeApiToken() ){
            self.changeMessage('Please enter an API token.', 'text-danger');
            return;
        }

        return osfHelpers.postJSON(
            self.account_url,
            ko.toJS({
                make_api_token: self.makeApiToken(),
            })
        ).done(function() {
            self.clearModal();
            $modal.modal('hide');
            self.updateAccounts();

        }).fail(function(xhr, textStatus, error) {
            var errorMessage = (xhr.status === 400 && xhr.responseJSON.message !== undefined) ? xhr.responseJSON.message : 'auth error';
            self.changeMessage(errorMessage, 'text-danger');
            Raven.captureMessage('Could not authenticate with Make', {
                extra: {
                    url: self.account_url,
                    textStatus: textStatus,
                    error: error
                }
            });
        });
    };

    self.updateAccounts = function() {
        return $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            self.accounts($.map(data.accounts, function(account) {
                var externalAccount =  new ExternalAccount(account);
                externalAccount.makeApiToken = account.make_api_token;
                return externalAccount;
            }));
            $('#make-header').osfToggleHeight({height: 160});
        }).fail(function(xhr, status, error) {
            self.changeMessage('user setting error', 'text-danger');
            Raven.captureMessage('Error while updating addon account', {
                extra: {
                    url: url,
                    status: status,
                    error: error
                }
            });
        });
    };

    self.askDisconnect = function(account) {
        var self = this;
        bootbox.confirm({
            title: _('Disconnect Make Account?'),
            message: sprintf(_('<p class="overflow">Are you sure you want to disconnect the Make account <strong>%1$s</strong>? This will revoke access to Make for all projects associated with this account.</p>'), osfHelpers.htmlEscape(account.name)),
            callback: function (confirm) {
                if (confirm) {
                    self.disconnectAccount(account);
                }
            },
            buttons:{
                confirm:{
                    label:_('Disconnect'),
                    className:'btn-danger'
                }
            }
        });
    };

    self.disconnectAccount = function(account) {
        var self = this;
        var url = '/api/v1/oauth/accounts/' + account.id + '/';
        var request = $.ajax({
            url: url,
            type: 'DELETE'
        });
        request.done(function(data) {
            self.updateAccounts();
        });
        request.fail(function(xhr, status, error) {
            Raven.captureMessage('Error while removing addon authorization for ' + account.id, {
                extra: {
                    url: url,
                    status: status,
                    error: error
                }
            });
        });
        return request;
    };

    self.selectionChanged = function() {
        self.changeMessage('','');
    };

    self.updateAccounts();

}

$.extend(ViewModel.prototype, ChangeMessageMixin.prototype);

function MakeUserConfig(selector, url) {
    // Initialization code
    var self = this;
    self.selector = selector;
    self.url = url;
    // On success, instantiate and bind the ViewModel
    self.viewModel = new ViewModel(url);
    osfHelpers.applyBindings(self.viewModel, self.selector);
}

module.exports = {
    MakeViewModel: ViewModel,
    MakeUserConfig: MakeUserConfig
};

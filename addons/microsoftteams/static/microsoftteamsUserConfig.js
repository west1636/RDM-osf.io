/**
* Module that controls the Microsoft 365 user settings. Includes Knockout view-model
* for syncing data.
*/

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');
require('js/osfToggleHeight');

var language = require('js/osfLanguage').Addons.microsoftteams;
var osfHelpers = require('js/osfHelpers');
var addonSettings = require('js/addonSettings');
var ChangeMessageMixin = require('js/changeMessage');
var ExternalAccount = addonSettings.ExternalAccount;

var _ = require('js/rdmGettext')._;
var sprintf = require('agh.sprintf').sprintf;

var $modal = $('#microsoftteamsCredentialsModal');

function ViewModel(url) {
    var self = this;

    self.properName = 'Microsoft 365';
    self.accessKey = ko.observable();
    self.secretKey = ko.observable();
    self.account_url = '/api/v1/settings/microsoftteams/accounts/';
    self.accounts = ko.observableArray();

    self.microsoftteamsTenant = ko.observable();
    self.microsoftteamsClientId = ko.observable();
    self.microsoftteamsClientSecret = ko.observable();
	
    self.userGuid = ko.observable();
    self.microsoftTeamsUserName = ko.observable();
    self.microsoftTeamsMail = ko.observable();
    self.webexMeetingsDisplayName = ko.observable();
    self.webexMeetingsMail = ko.observable();
    self.userGuidToDelete = ko.observable();

    ChangeMessageMixin.call(self);

    /** Reset all fields from Microsoft 365 credentials input modal */
    self.clearModal = function() {
        self.message('');
        self.messageClass('text-info');
        self.microsoftteamsTenant(null);
        self.microsoftteamsClientId(null);
        self.microsoftteamsClientSecret(null);
    };
    /** Send POST request to authorize Microsoft 365 */
    self.connectAccount = function() {
        // Selection should not be empty
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

        return osfHelpers.postJSON(
            self.account_url,
            ko.toJS({
                microsoftteams_tenant: self.microsoftteamsTenant(),
                microsoftteams_client_id: self.microsoftteamsClientId(),
                microsoftteams_client_secret: self.microsoftteamsClientSecret(),
            })
        ).done(function() {
            self.clearModal();
            $modal.modal('hide');
            self.updateAccounts();

        }).fail(function(xhr, textStatus, error) {
            var errorMessage = (xhr.status === 400 && xhr.responseJSON.message !== undefined) ? xhr.responseJSON.message : 'auth error';
            self.changeMessage(errorMessage, 'text-danger');
            Raven.captureMessage('Could not authenticate with Microsoft 365', {
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
                externalAccount.microsoftteamsTenant = account.microsoftteamsTenant;
                externalAccount.microsoftteamsClientId = account.microsoftteamsClientId;
                externalAccount.microsoftteamsClientSecret = account.microsoftteamsClientSecret;
                return externalAccount;
            }));
            $('#microsoftteams-header').osfToggleHeight({height: 160});
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
            title: _('Disconnect Microsoft 365 Account?'),
            message: sprintf(_('<p class="overflow">Are you sure you want to disconnect the Microsoft 365 account <strong>%1$s</strong>? This will revoke access to Microsoft 365 for all projects associated with this account.</p>'), osfHelpers.htmlEscape(account.name)),
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

function MicrosoftTeamsUserConfig(selector, url) {
    // Initialization code
    var self = this;
    self.selector = selector;
    self.url = url;
    // On success, instantiate and bind the ViewModel
    self.viewModel = new ViewModel(url);
    osfHelpers.applyBindings(self.viewModel, self.selector);
}

module.exports = {
    MicrosoftTeamsViewModel: ViewModel,
    MicrosoftTeamsUserConfig: MicrosoftTeamsUserConfig
};

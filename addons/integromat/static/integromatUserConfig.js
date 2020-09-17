/**
* Module that controls the Integromat user settings. Includes Knockout view-model
* for syncing data.
*/

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var bootbox = require('bootbox');
require('js/osfToggleHeight');

var language = require('js/osfLanguage').Addons.integromat;
var osfHelpers = require('js/osfHelpers');
var addonSettings = require('js/addonSettings');
var oop = require('js/oop');
var OAuthAddonSettingsViewModel = require('js/addonSettings.js').OAuthAddonSettingsViewModel;

var ExternalAccount = addonSettings.ExternalAccount;

var $modal = $('#integromatCredentialsModal');


var ViewModel = oop.extend(OAuthAddonSettingsViewModel,{
    constructor: function(url){
        var self = this;
        self.name = 'integromat';
        self.properName = 'Integromat';
        self.accounts = ko.observableArray();
        self.message = ko.observable('');
        self.messageClass = ko.observable('');
        const otherString = 'Other (Please Specify)';

        self.url = url;
        self.properName = 'Integromat';
        self.integromatApiToken = ko.observable();
        self.urls = ko.observable({});
        self.hosts = ko.observableArray([]);
        self.selectedHost = ko.observable();    // Host specified in select element
        self.customHost = ko.observable();      // Host specified in input element
        // Whether the initial data has been loaded
        self.loaded = ko.observable(false);

        self.showApiTokenInput = ko.pureComputed(function() {
            return Boolean(self.selectedHost());
        });
    },
    clearModal: function() {
        /** Reset all fields from Integromat host selection modal */
        var self = this;
        self.message('');
        self.messageClass('text-info');
        self.integromatApiToken(null);

    },
    updateAccounts: function() {
        var self = this;
        var url = self.urls().accounts;
        var request = $.get(url);
        request.done(function(data) {
            self.accounts($.map(data.accounts, function(account) {
                var externalAccount =  new ExternalAccount(account);
                return externalAccount;
            }));
            $('#integromat-header').osfToggleHeight({height: 160});
        });
        request.fail(function(xhr, status, error) {
            Raven.captureMessage('Error while updating addon account', {
                extra: {
                    url: url,
                    status: status,
                    error: error
                }
            });
        });
        return request;
    },
    connectAccount : function() {
        var self = this;
        // Selection should not be empty
        if (!self.integromatApiToken() ){
            self.changeMessage('Please enter an API token.', 'text-danger');
            return;
			}
/*
        return $osf.postJSON(
            self.urls().create, {
                integromat_api_token: self.integromatApiToken()
				}
*/
        var url = self.urls().create;
        return osfHelpers.postJSON(
            url,
            ko.toJS({
                integromat_api_token: self.integromatApiToken()
            })
        ).done(function() {
            self.clearModal();
            $modal.modal('hide');
            $('#integromatCredentialsModal').modal('hide');
            self.updateAccounts();
            self.authSuccessCallback();

        }).fail(function(xhr, textStatus, error) {
            var errorMessage = (xhr.status === 401) ? '401' : 'Invalid integromat server';
            self.changeMessage(errorMessage, 'text-danger');
            Raven.captureMessage('Could not authenticate with Integromat', {
                url: self.url,
                textStatus: textStatus,
                error: error
            });
        });
    },
    authSuccessCallback: function() {
        // Override for NS-specific auth success behavior
        // TODO: generalize this when rewriting addon configs for ember
        return;
    },
    fetch: function() {
        // Update observables with data from the server
        var self = this;
        $.ajax({
            url: self.url,
            type: 'GET',
            dataType: 'json'
        }).done(function (response) {
            var data = response.result;
            self.urls(data.urls);
            self.loaded(true);
            self.updateAccounts();
        }).fail(function (xhr, textStatus, error) {
            self.setMessage('Could not retrieve settings', 'text-danger');
            Raven.captureMessage('Could not GET Integromat settings', {
                extra: {
                    url: self.url,
                    textStatus: textStatus,
                    error: error
                }
            });
        });
    },
    selectionChanged: function() {
        var self = this;
        self.setMessage('','');
    }
});

function IntegromatUserConfig(selector, url) {
    // Initialization code
    var self = this;
    self.selector = selector;
    self.url = url;
    // On success, instantiate and bind the ViewModel
    self.viewModel = new ViewModel(url);
    osfHelpers.applyBindings(self.viewModel, self.selector);
}

module.exports = {
    IntegromatUserViewModel: ViewModel,
    IntegromatUserConfig: IntegromatUserConfig    // for backwards-compat
};

'use strict';

var ko = require('knockout');
var $ = require('jquery');
var Raven = require('raven-js');
var OauthAddonNodeConfigViewModel = require('js/oauthAddonNodeConfig')._OauthAddonNodeConfigViewModel;
var language = require('js/osfLanguage').Addons.owncloud;
var osfHelpers = require('js/osfHelpers');
var oop = require('js/oop');
var $modal = $('#integromatCredentialsModal');

var m = require('mithril');
var bootbox = require('bootbox');
var Raven = require('raven-js');

var $osf = require('js/osfHelpers');

var nodeApiUrl = window.contextVars.node.urls.api;

var connectExistingAccount = function(accountId) {
    $osf.putJSON(
            nodeApiUrl + 'integromat/user_auth/',
            {'external_account_id': accountId}
        ).done(function() {
                if($osf.isIE()){
                    window.location.hash = '#configureAddonsAnchor';
                }
                window.location.reload();
        }).fail(function(){
            $.osf.growl('Error', 'Your account could not be connected, if the problem persists you may need to' +
             ' reconnect to integromat or contact us at ' + $.osf.osfSupportLink() + '.');
            Raven.captureMessage('Unexpected error occurred in JSON request');
        });
};

var askImport = function() {
    $.get('/api/v1/settings/integromat/accounts/'
    ).done(function(data){

        var accounts = data.accounts.map(function(account) {
            return {
                name: account.display_name,
                id: account.id
            };
        });


        bootbox.confirm({
                title: 'Link Integromat Account?',
                message: 'Are you sure you want to link your Integromat account with this project?',
                callback: function(confirmed) {
                    if (confirmed) {
                        connectExistingAccount(accounts[0].id);
                    }
                },
                buttons: {
                    confirm: {
                        label:'Link',
                    }
                }
		});
    }).fail(function(xhr, textStatus, error) {
        displayError('Could not GET Integromat accounts for user.');
    });
};

$(document).ready(function() {

    $('#integromatImportToken').on('click', function() {
        askImport();
    });

    $('#integromatRemoveToken').on('click', function() {
        bootbox.confirm({
            title: 'Disconnect Integromat Account?',
            message: 'Are you sure you want to remove this Integromat account?',
            callback: function(confirm) {
                if(confirm) {
                    $.ajax({
                    type: 'DELETE',
                    url: nodeApiUrl + 'integromat/user_auth/'
                }).done(function() {
                    window.location.reload();
                }).fail(
                    $osf.handleJSONError
                );
                }
            },
            buttons:{
                confirm:{
                    label: 'Disconnect',
                    className: 'btn-danger'
                }
            }
        });
    });

});


var integromatViewModel = oop.extend(OauthAddonNodeConfigViewModel,{
    constructor: function(addonName, url, selector, folderPicker, opts, tbOpts){
        var self = this;
        self.super.constructor(addonName, url, selector, folderPicker, tbOpts);
        self.super.construct.call(self, addonName, url, selector, folderPicker, opts, tbOpts);

        self.integromatApiToken = ko.observable();
//		self.urls = ko.observable({});


    },
    clearModal : function() {
        var self = this;
        self.integromatApiToken(null);
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
        askImport();
    }
});

// Public API
function integromatNodeConfig(addonName, selector, url, folderPicker, opts, tbOpts) {
    var self = this;
    self.url = url;
    self.folderPicker = folderPicker;
    opts = opts || {};
    tbOpts = tbOpts || {};
    self.viewModel = new integromatViewModel(addonName, url, selector, folderPicker, opts, tbOpts);
    self.viewModel.updateFromData();
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = {
    IntegromatViewModel: integromatViewModel,
    integromatNodeConfig: integromatNodeConfig
};

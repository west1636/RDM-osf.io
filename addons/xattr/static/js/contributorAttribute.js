'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
require('knockout.validation');
require('knockout-sortable');
var $osf = require('js/osfHelpers');
var ExtendedContribManager = require('./extendedContribManager');


// "Local" variables
var ctx = window.contextVars;

module.exports = {
    submitData: function () {
        var data = {
            en: {
                contributors: manager.extendedContributorViewModel.contributors
            }
        };

        return data;
    }
};

var manager = new ExtendedContribManager(
    '#manageContributors',
    ctx.contributors,
    ctx.adminContributors,
    ctx.currentUser,
    ctx.isRegistration,
    '#manageContributorsTable',
    '#adminContributorsTable'
);

window.editContributor = function (id) {
    manager.extendedContributorViewModel.editContributor(id);
};

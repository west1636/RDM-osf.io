'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
require('jquery-ui');
require('knockout-sortable');
var ContribManager = require('js/contribManager');
var $osf = require('js/osfHelpers');
require('js/filters');


ko.utils.clone = function (obj) {
    var target = new obj.constructor();
    for (var prop in obj) {
        var propVal = obj[prop];
        if (ko.isObservable(propVal)) {
            var val = propVal();
            if ($.type(val) == 'object') {
                target[prop] = ko.utils.clone(val);
                continue;
            }
            target[prop](val);
        } else {
            target[prop] = propVal;
        }
    }
    return target;
};


function Alternative (data) {
    data = typeof data !== 'undefined' ? data : {};
    var self = this;

    self.value = ko.observable(data.value);
}

function Contributor (data) {
    data = typeof data !== 'undefined' ? data : {};
    var self = this;

    self.id = data.id;
    self.userName = data.userName;
    self.permission = ko.observable(data.permission);
    self.visible = ko.observable(data.visible);
    self.contributorType = ko.observable(data.contributorType);
    self.contributorRemarks = ko.observable(data.contributorRemarks);
    self.assignSituation = ko.observable(data.assignSituation);
    self.representationSetting = ko.observable(data.representationSetting);
    self.name = ko.observable(data.name);
    self.alternatives = ko.observableArray(data.alternatives);
    self.organizationType = ko.observable(data.organizationType);
    self.idpId = ko.observable(data.idpId);
    self.researchOrganizationId = ko.observable(data.researchOrganizationId);
    self.organizationRecognitionId = ko.observable(data.organizationRecognitionId);
    self.storageDepOrganizationId = ko.observable(data.storageDepOrganizationId);
    self.version = ko.observable(data.version);

    self.addAlternative = function () {
        self.alternatives.push(new Alternative({}));
    };

    self.removeAlternative = function (alternative) {
        self.alternatives.remove(alternative);
    };
}

function ExtendedContributorViewModel(data) {
    var self = this;

    self.contributors = ko.observableArray(data.contributors.map(function (contributor) {
        contributor.alternatives = contributor.alternatives.map(function (alternative) {
            return new Alternative(alternative);
        });
        return new Contributor(contributor);
    }));
    self.editingContributor = ko.observable(false);
    self.contribInstance = ko.observable(new Contributor({}));

    self.editContributor = function (id) {
        self.editingContributor(true);

        var contributor = null;
        for (var i = 0; i < self.contributors().length; i++) {
            if (self.contributors()[i].id == id) {
                contributor = self.contributors()[i];
                break;
            }
        }
        if (contributor !== null) {
            //self.contribInstance(ko.utils.clone(contributor));
            self.contribInstance(contributor);
        } else {
            console.warn('Contributor not found!?');
        }
    };

    self.saveContributor = function () {
        self.editingContributor(false);

        var contribIndex = null;
        for (var i = 0; i < self.contributors().length; i++) {
            if (self.contributors()[i].id == self.contribInstance().id) {
                contribIndex = i;
                break;
            }
        }

        // Create
        if (contribIndex === null) {
            self.contributors.push(self.contribInstance());
        } else { // Edit
        }
    };

    self.cancelContributor = function () {
        self.editingContributor(false);
    };
}

// Inherits ContribManager
function ExtendedContribManager(selector, contributors, adminContributors, user, isRegistration, table, adminTable) {
    var self = this;

    ContribManager.call(self, selector, contributors, adminContributors, user, isRegistration, table, adminTable);

    // Extended contributors default data
    self.extendedContributors = contributors.map(function (contributor) {
        return {
            id: contributor.id,
            userName: contributor.fullname,
            permission: false,
            visible: true,
            contributorRemarks: 'Sample Contributor Remarks',
            assignSituation: 'Sample Contributor Assign Situation',
            name: 'John Contributor',
            alternatives: [{}],
            version: true
        };
    });
    var existing_contributors = JSON.parse($('#existing_contributors').val());
    if (existing_contributors) {
        existing_contributors = existing_contributors['en'].contributors;
        // Merge current contributors and extended contributors
        for (var i = 0; i < self.extendedContributors.length; i++) {
            for (var j = 0; j < existing_contributors.length; j++) {
                if (self.extendedContributors[i].id == existing_contributors[j].id) {
                    self.extendedContributors[i] = existing_contributors[j];
                    break;
                }
            }
        }
    }

    self.extendedContributorViewModel = new ExtendedContributorViewModel({
        contributors: self.extendedContributors
    });

    $osf.applyBindings(self.extendedContributorViewModel, '#en_contributors-extensions');
}

ExtendedContribManager.prototype = Object.create(ContribManager.prototype);

module.exports = ExtendedContribManager;

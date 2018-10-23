'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
require('knockout.validation');
require('knockout-sortable');
var $osf = require('js/osfHelpers');


// "Local" variables
var ctx = window.contextVars;

// Creating an array with the languages to be used in the script
// So we don't need to implement everthing twice,
// One for each language
var langs = ['en', 'ja'];
var lang, i;
var now = new Date();


module.exports = {
    submitData: function () {
        var data = {
            'en': {
                'fundings': en_fundings.fundings
            },
            'ja': {
                'fundings': ja_fundings.fundings
            }
        };

        return data;
    }
};


function Applicant (data) {
    var self = this;

    self.name = ko.observable(data.name);
    self.alternativeName = ko.observable(data.alternativeName);
    self.organization = ko.observable(data.organization);
    self.department = ko.observable(data.department);
    self.awardTitle = ko.observable(data.awardTitle);
    self.address = ko.observable(data.address);
    self.telephone = ko.observable(data.telephone);
    self.email = ko.observable(data.email);
}

function Payment (data) {
    var self = this;

    self.paymentYear = ko.observable(data.paymentYear);
    self.directCosts = ko.observable(data.directCosts);
    self.indirectCosts = ko.observable(data.indirectCosts);
}

function Funding (data) {
    var self = this;

    self.funderId = ko.observable(data.funderId);
    self.funderReference = ko.observable(data.funderReference);
    self.awardTitle = ko.observable(data.awardTitle);
    self.budgetCategory = ko.observable(data.budgetCategory);
    self.fundingProgramme = ko.observable(data.fundingProgramme);
    self.status = ko.observable(data.status);
    self.availableFunds = ko.observable(data.availableFunds);
    self.startDate = ko.observable(data.startDate);
    self.endDate = ko.observable(data.endDate);
    self.applicants = ko.observableArray(data.applicants);
    self.funderSubjectOutline = ko.observable(data.funderSubjectOutline);
    self.funderSubjectResultOutline = ko.observable(data.funderSubjectResultOutline);
    self.funderSubjectReachDegree = ko.observable(data.funderSubjectReachDegree);
    self.funderPropulsionScheme = ko.observable(data.funderPropulsionScheme);
    self.funderEvaluationMark = ko.observable(data.funderEvaluationMark);
    self.funderEvaluationOutline = ko.observable(data.funderEvaluationOutline);
    self.payments = ko.observableArray(data.payments);

    self.addApplicant = function () {
        self.applicants.push(new Applicant({}));
    }

    self.removeApplicant = function (applicant) {
        self.applicants.remove(applicant);
    }

    self.addPayment = function () {
        self.payments.push(new Payment({
            paymentYear: now.getFullYear(),
            directCosts: 0,
            indirectCosts: 0
        }));
    }

    self.removePayment = function (payment) {
        self.payments.remove(payment);
    }

    self.totalDirectCosts = ko.computed(function () {
        var total = 0;
        for (var i = 0; i < self.payments().length; i++) {
            if (!isNaN(self.payments()[i].directCosts())) {
                total += parseInt(self.payments()[i].directCosts());
            }
        }
        return total;
    }, self);

    self.totalIndirectCosts = ko.computed(function () {
        var total = 0;
        for (var i = 0; i < self.payments().length; i++) {
            if (!isNaN(self.payments()[i].indirectCosts())) {
                total += parseInt(self.payments()[i].indirectCosts());
            }
        }
        return total;
    }, self);
}

function FundingsViewModel (lang) {
    var self = this;

    self.fundings = ko.observableArray([]);
    self.addingFunder = ko.observable(false);
    self.editingFunder = ko.observable(false);
    self.funderInstance = ko.observable(new Funding({
        funderReference: 'Sample Funder Reference',
        awardTitle: 'Sample Award Title',
        fundingProgramme: 'Sample Funding Programee',
        startDate: '2017-08-01',
        endDate: '2018-10-01',
        applicants: [
            new Applicant({
                name: 'John'
            })
        ],
        funderSubjectReachDegree: 'Sample Subject Reach Degree',
        payments: [
            new Payment({
                paymentYear: now.getFullYear(),
                directCosts: 0,
                indirectCosts: 0
            })
        ]
    }));

    self.showAddFunderForm = function () {
        $('#' + lang + '_add-modal').modal('toggle');
        self.addingFunder(true);
        self.funderInstance(new Funding({
            funderReference: 'Sample Funder Reference',
            awardTitle: 'Sample Award Title',
            fundingProgramme: 'Sample Funding Programee',
            startDate: '2017-08-01',
            endDate: '2018-10-01',
            applicants: [
                new Applicant({
                    name: 'John'
                })
            ],
            funderSubjectReachDegree: 'Sample Subject Reach Degree',
            payments: [
                new Payment({
                    paymentYear: now.getFullYear(),
                    directCosts: 0,
                    indirectCosts: 0
                })
            ]
        }));
    }

    self.showEditFunderForm = function (funder) {
        self.editingFunder(true);
        self.funderInstance(funder);
    }

    self.saveFunder = function () {
        if (self.editingFunder()) {
            self.editingFunder(false);
            window.location.hash = '#' + lang + '_fundings';
        } else { // If there are no fundings, allow saving without clicking 'Add' button
            self.fundings.push(self.funderInstance());
            self.addingFunder(false);
            window.location.hash = '#' + lang + '_fundings';
        }
    }

    self.cancelFunder = function () {
        self.addingFunder(false);
        self.editingFunder(false);
        window.location.hash = '#' + lang + '_fundings';
    }

    self.removeFunder = function (funder) {
        self.fundings.remove(funder);
    }

    // Load existing fundings
    var existing_fundings = JSON.parse($('#existing_fundings').val());
    if (existing_fundings) {
        existing_fundings = existing_fundings[lang].fundings;
        self.fundings(existing_fundings.map(function (funding) {
            funding.applicants = funding.applicants.map(function (applicant) {
                return new Applicant(applicant);
            });
            funding.payments = funding.payments.map(function (payment) {
                return new Payment(payment);
            });
            return new Funding(funding);
        }));
    }
}

if ($('#en_fundingsExtensions').length) {
    var en_fundings = new FundingsViewModel('en');
    $osf.applyBindings(en_fundings, '#en_fundingsExtensions');
}

if ($('#ja_fundingsExtensions').length) {
    var ja_fundings = new FundingsViewModel('ja');
    $osf.applyBindings(ja_fundings, '#ja_fundingsExtensions');
}

'use strict';
var $ = require('jquery');
var ko = require('knockout');
var $osf = require('js/osfHelpers');


function ViewModel(url, data) {
    var self = this;

    self.title = ko.observable(data.title);
    self.affiliation = ko.observable(data.affiliation);
    self.projectType = ko.observable(data.projectType);
    self.projectStatus = ko.observable(data.projectStatus);

    self.loaded = ko.observable(true);
    self.connected = ko.observable(true);
    self.complete = ko.observable(true);

    // Flashed messages
    self.message = ko.observable('');
    self.messageClass = ko.observable('text-info');

    /** Change the flashed status message */
    self.changeMessage = function(text, css, timeout) {
        self.message(text);
        var cssClass = css || 'text-info';
        self.messageClass(cssClass);
        if (timeout) {
            // Reset message after timeout period
            setTimeout(function() {
                self.message('');
                self.messageClass('text-info');
            }, timeout);
        }
    };
}

function extractData(rawData) {
    var extractedData = {};
    if (rawData) {
        var parsedData = JSON.parse(rawData);
        if (parsedData.hasOwnProperty('data')) {
            extractedData = parsedData['data'];
        }
    }
    return extractedData;
}

function existingData() {
    var project = extractData($('#xattr-project').val());
    var fundings = extractData($('#xattr-fundings').val());
    var contributors = extractData($('#xattr-contributors').val());
    var status = {'1': '開始', '12': '終了'};
    return {
        title: project.ja.title,
        affiliation: project.ja.organizationUnit,
        projectType: project.ja.researchField,
        projectStatus: status[project.ja.status]
    };
}

// Public API
function XattrWidget(selector, url) {
    var self = this;
    self.viewModel = new ViewModel(url, existingData());
    $osf.applyBindings(self.viewModel, selector);
}

module.exports = XattrWidget;

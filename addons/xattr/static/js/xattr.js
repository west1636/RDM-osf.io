'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
require('knockout.validation');
require('knockout-sortable');
var $osf = require('js/osfHelpers');
var ctx = window.contextVars;

var projectAttribute = require('./projectAttribute.js');
var fundingAttribute = require('./fundingAttribute.js');
var contributorAttribute = require('./contributorAttribute.js');


$('#save-data').click(function () {
    var url = '/api/v1/project' + window.location.pathname + '/';
    var data = {
        projectAttribute: projectAttribute.submitData(),
        fundingAttribute: fundingAttribute.submitData(),
        contributorAttribute: contributorAttribute.submitData()
    };
    // console.log(JSON.parse(ko.toJSON(data)));
    $.ajax({
        url: url,
        type: 'POST',
        data: ko.toJSON(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (response) {
            if (response['Status'] == 'OK') {
                $osf.growl('Settings saved!', 'Your settings has been successfully saved!', 'success');
            } else {
                $osf.growl('Error', 'There was an error while saving.', 'danger');
            }
        },
        error: function () {
            $osf.growl('Error', 'There was an error while saving.', 'danger');
        }
    });
});

$('#reset-data').click(function () {
    window.location.href = window.location.href.split('#')[0];
});

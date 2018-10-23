'use strict';

var $ = require('jquery');
var ko = require('knockout');
var bootbox = require('bootbox');
require('knockout.validation');
require('knockout-sortable');
var $osf = require('js/osfHelpers');
var ctx = window.contextVars;


// Creating an array with the languages to be used in the script
// So we don't need to implement everthing twice,
// One for each language
var langs = ['en', 'ja'];
var lang, i;


function submitData () {
var data = {};

for (i in langs) {
    lang = langs[i];
    data[lang] = {
	'rangeType': [],
	'range': []
    };
    var form = $('#' + lang + '_userAttribute');
    var inputs = form.find('.form-control').filter(':visible');

    inputs.each(function () {
	var fieldName = $(this).attr('name');
	// Normal fields
	if (fieldName != 'rangeType' && fieldName != 'range') {
	    data[lang][fieldName] = $(this).val();
	} else { // Array fields
	    data[lang][fieldName].push($(this).val());
	}
    });
}
console.log(data)
return data;
}


$('#save-data').click(function () {
    var url = '/api/v1' + window.location.pathname;
    console.log(submitData()) 
    var data = {
        'userAttribute': submitData()
    };
    console.log(data);
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function () {
            console.warn('Server Error');
        }
    });
});

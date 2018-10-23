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


module.exports = {
    submitData: function () {
        var data = {};

        for (i in langs) {
            lang = langs[i];
            data[lang] = {
                'rangeType': [],
                'range': []
            };
            var form = $('#' + lang + '_projectAttribute');
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

        return data;
    }
};


for (i in langs) {
    lang = langs[i];

    var addRangeButton = $('#' + lang + '-add-range');
    addRangeButton.click(function () {
        var lang = $(this).attr('id').substr(0, 2);
        var rangeList = $('#' + lang + '-range-list');
        var rangeBlockClone = rangeList.find('.scripted').clone();
        rangeBlockClone = rangeBlockClone.removeClass('scripted');

        // Remove event
        var removeButton = rangeBlockClone.find('.remove-range');
        removeButton.click(function () {
            var rangeBlock = $(this).parent().parent();
            rangeBlock.remove();
        });

        rangeBlockClone.appendTo(rangeList);
    });

    // Create one by default
    var rangeList = $('#' + lang + '-range-list');
    rangeList = rangeList.find('.panel-default').filter(':visible');
    if (rangeList.length == 0) {
        addRangeButton.click();
    }
}

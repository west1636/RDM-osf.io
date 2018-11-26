'use strict';

var $ = require('jquery');
var nodeApiUrl = window.contextVars.node.urls.api;
var timestampCommon = require('./timestamp-common.js');


$(document).ready(function () {
    timestampCommon.initList();
});

$(function () {
    var btnVerify_onclick = function () {
        if ($('#btn-verify').attr('disabled') !== undefined || $('#btn-addtimestamp').attr('disabled') !== undefined) {
            return false;
        }
        timestampCommon.verify({
            urlVerify: 'json/',
            urlVerifyData: nodeApiUrl + 'timestamp/timestamp_error_data/',
            method: 'GET'
        });
    };

    var btnAddtimestamp_onclick = function () {
        if ($('#btn-verify').attr('disabled') !== undefined || $('#btn-addtimestamp').attr('disabled') !== undefined) {
            return false;
        }
        timestampCommon.add({
            url: nodeApiUrl + 'timestamp/add_timestamp/',
            method: 'GET'
        });
    };

    $('#addTimestampAllCheck').on('change', function () {
        $('input[id=addTimestampCheck]').prop('checked', this.checked);
    });

    var document_onready = function () {
        $('#btn-verify').on('click', btnVerify_onclick);
        $('#btn-addtimestamp').on('click', btnAddtimestamp_onclick).focus();
    };

    $(document).ready(document_onready);
    $('#timestamp_errors_spinner').hide();
});

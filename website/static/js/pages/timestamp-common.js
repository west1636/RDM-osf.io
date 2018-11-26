'use strict';

var $ = require('jquery');
var Raven = require('raven-js');
var List = require('list.js');


var verify = function (params) {
    $('#btn-verify').attr('disabled', true);
    $('#btn-addtimestamp').attr('disabled', true);
    $('#timestamp_errors_spinner').text('Storage files list gathering ...');
    $('#timestamp_errors_spinner').show();

    var postData = {};
    var successCnt = 0;
    var fileCnt, i;

    // Get files list
    $.ajax({
        url: params.urlVerify,
        data: postData,
        dataType: 'json',
        method: params.method
    }).done(function (data) {
        var projectFileList = data.provider_list;

        // Count the number of files
        fileCnt = projectFileList.reduce(function (accumulator, current) {
            return accumulator + current.provider_file_list.length;
        }, 0);

        // Verify files for each provider
        for (i = 0; i < projectFileList.length; i++) {
            successCnt = verifyProviderFiles(params, projectFileList[i], fileCnt, successCnt);
        }
    }).fail(function (xhr, textStatus, error) {
        Raven.captureMessage('Timestamp Add Error', {
            extra: {
                url: params.urlVerify,
                textStatus: textStatus,
                error: error
            }
        });
        $('#btn-verify').removeAttr('disabled');
        $('#btn-addtimestamp').removeAttr('disabled');
        $('#timestamp_errors_spinner').text('Error: Storage files list gathering failed');
    });
};

var verifyProviderFiles = function (params, providerInfo, fileCnt, successCnt) {
    var i, fileList;

    fileList = providerInfo.provider_file_list;
    for (i = 0; i < fileList.length; i++) {
        var postData = {
            'provider': providerInfo.provider,
            'file_id': fileList[i].file_id,
            'file_path': fileList[i].file_path,
            'file_name': fileList[i].file_name,
            'version': fileList[i].version
        };
        $.ajax({
            url:  params.urlVerifyData,
            data: postData,
            dataType: 'json',
            method: params.method
        }).done(function () {
            successCnt++;
            $('#timestamp_errors_spinner').text('Verification files : ' + successCnt + ' / ' + fileCnt + ' ...');
            if (successCnt === fileCnt) {
                $('#timestamp_errors_spinner').text('Verification (100%) and Refreshing...');
                window.location.reload();
            }
        }).fail(function (xhr, status, error) {
            if (successCnt === fileCnt) {
                Raven.captureMessage('Timestamp Add Error: ' + fileList[i].file_path, {
                    extra: {
                        url: params.urlVerifyData,
                        status: status,
                        error: error
                    }
                });
                $('#btn-verify').removeAttr('disabled');
                $('#btn-addtimestamp').removeAttr('disabled');
                $('#timestamp_errors_spinner').text('Error: ' + fileList[i].file_path);
            }
        });
    }
    return successCnt;
};

var add = function (params) {
    var fileList = $('#timestamp_error_list .addTimestamp').map(function () {
        if ($(this).find('#addTimestampCheck').prop('checked')) {
            return {
                provider: $(this).find('#provider').val(),
                file_id: $(this).find('#file_id').val(),
                file_path: $(this).find('#file_path').val(),
                version: $(this).find('#version').val(),
                file_name: $(this).find('#file_name').val(),
            };
        }
        return null;
    });

    if (fileList.length === 0) {
        return false;
    }

    $('#btn-verify').attr('disabled', true);
    $('#btn-addtimestamp').attr('disabled', true);
    $('#timestamp_errors_spinner').text('Addtimestamp loading ...');
    $('#timestamp_errors_spinner').show();

    var successCnt = 0;
    for (var i = 0; i < fileList.length; i++) {
        var post_data = {
            'provider': fileList[i].provider,
            'file_id': fileList[i].file_id,
            'file_path': fileList[i].file_path,
            'file_name': fileList[i].file_name,
            'version': fileList[i].version
        };
        $.ajax({
            url: params.url,
            data: post_data,
            dataType: 'json',
            method: params.method
        }).done(function () {
            successCnt++;
            $('#timestamp_errors_spinner').text('Adding Timestamp files : ' + successCnt + ' / ' + fileList.length + ' ...');
            if (successCnt === fileList.length) {
                $('#timestamp_errors_spinner').text('Added Timestamp (100%) and Refreshing...');
                window.location.reload();
            }
        }).fail(function (xhr, status, error) {
            Raven.captureMessage('Timestamp Add Error: ' + fileList[i].file_path, {
                extra: {
                    url: params.url,
                    status: status,
                    error: error
                }
            });
            $('#btn-verify').removeAttr('disabled');
            $('#btn-addtimestamp').removeAttr('disabled');
            $('#timestamp_errors_spinner').text('Error : Timestamp Add Failed');
        });
    }
};

function initList() {
    var list = new List('timestamp-form', {
        valueNames: ['operator_user', 'operator_date'],
    });

    var userFilterSelect = document.getElementById('userFilterSelect');

    var alreadyAdded = [''];
    var users = list.items.map(function(i) {return i.values().operator_user;});
    for (var i = 0; i < users.length; i++) {
        var userName = users[i];
        if (!alreadyAdded.includes(userName)) {
            var option = document.createElement('option');
            option.value = userName;
            option.textContent = userName;
            userFilterSelect.add(option);
            alreadyAdded.push(userName);
        }
    }

    document.getElementById('applyFiltersButton').addEventListener('click', function() {
        var userName = userFilterSelect.value;
        var userNameFilter = function(i) {return !userName || (!i.values().operator_user || (i.values().operator_user === userName));};
        list.filter(userNameFilter);
    });
}

module.exports = {
    verify: verify,
    add: add,
    initList: initList,
};

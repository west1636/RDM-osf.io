'use strict';

var $ = require('jquery');
var Raven = require('raven-js');
var List = require('list.js');
var $osf = require('js/osfHelpers');

var DOWNLOAD_FILENAME = 'timestamp_errors';
var HEADERS_ORDER = [
    'file_path', 'provider', 'version'
];
var HEADERS_NAME = {
    provider: 'Provider',
    file_id: 'File ID',
    file_path: 'File Path',
    file_name: 'File Name',
    version: 'Version'
};


function newLine() {
    if (window.navigator.userAgent.indexOf('Windows NT') !== -1) {
        return '\r\n';
    }
    return '\n';
}

var NEW_LINE = newLine();

var verify = function (params) {
    $('#btn-verify').attr('disabled', true);
    $('#btn-addtimestamp').attr('disabled', true);
    $('#timestamp_errors_spinner').text('Storage files list gathering ...');
    $('#timestamp_errors_spinner').show();

    var postData = {};
    var i;
    var count = {
        total: null,
        success: 0,
        fail: 0
    };

    // Get files list
    $.ajax({
        url: params.urlVerify,
        data: postData,
        dataType: 'json',
        method: params.method
    }).done(function (data) {
        var projectFileList = data.provider_list;

        // Count the number of files
        count.total = projectFileList.reduce(function (accumulator, current) {
            return accumulator + current.provider_file_list.length;
        }, 0);

        // Verify files for each provider
        for (i = 0; i < projectFileList.length; i++) {
            verifyProviderFiles(params, projectFileList[i], count);
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

var verifyProviderFiles = function (params, providerInfo, count) {
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
            count.success++;
            $('#timestamp_errors_spinner').text('Verification files : ' + count.success + ' / ' + count.total + ' ...');
            if (count.total === count.success) {
                $('#timestamp_errors_spinner').text('Verification (100%) and Refreshing...');
                window.location.reload();
            }
        }).fail(function (xhr, status, error) {
            count.fail++;
            if (count.success + count.fail === count.total) {
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

var download = function () {
    var fileFormat = $('#fileFormat').val();
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
    }).get();

    if (fileList.length === 0) {
        $osf.growl('Timestamp', 'Using the checkbox, please select the files to download.', 'danger');
        return false;
    }

    var fileContent;
    switch (fileFormat) {
        case 'csv':
            fileContent = generateCsv(fileList);
            saveTextFile(DOWNLOAD_FILENAME + '.csv', fileContent);
            break;
        case 'json-ld':
            fileContent = generateJson(fileList);
            saveTextFile(DOWNLOAD_FILENAME + '.json', fileContent);
            break;
        case 'rdf-xml':
            fileContent = generateXml(fileList);
            saveTextFile(DOWNLOAD_FILENAME + '.xml', fileContent);
            break;
    }
};

function generateCsv(fileList) {
    var content = '';

    // Generate header
    content += HEADERS_ORDER.map(function (headerName) {
        return HEADERS_NAME[headerName];
    }).join(',') + NEW_LINE;

    // Generate content
    content += fileList.map(function (file) {
        return HEADERS_ORDER.map(function (headerName) {
            return file[headerName];
        }).join(',');
    }).join(NEW_LINE);

    return content;
}

function generateJson(fileList) {
    // Update headers as defined in HEADERS_NAME
    fileList = fileList.map(function (file) {
        return HEADERS_ORDER.reduce(function (accumulator, current) {
            accumulator[HEADERS_NAME[current]] = file[current];
            return accumulator;
        }, {});
    });

    // Generate content
    return JSON.stringify(fileList, null, 2).replace(/\n/g, NEW_LINE);
}

function generateXml(fileList) {
    return JSON.stringify(fileList);
}

function saveTextFile(filename, content) {
    if (window.navigator.msSaveOrOpenBlob) {
        var blob = new Blob([content], {type: 'text/plain; charset=utf-8'});
        window.navigator.msSaveOrOpenBlob(blob, filename);
    }
    else {
        var element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain; charset=utf-8,' + encodeURI(content));
        element.setAttribute('download', filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    }
}

function initList() {

    document.querySelector('[type=reset]').addEventListener('click', function(event) {
        // when using polyfill only
        if (document.getElementById('startDateFilter').hasAttribute('data-has-picker')) {
            document.getElementById('startDateFilter').value='';
            document.getElementById('endDateFilter').value='';
        }
    });

    var list = new List('timestamp-form', {
        valueNames: ['operator_user', 'operator_date'],
    });

    var userFilterSelect = document.getElementById('userFilterSelect');

    var alreadyAdded = [''];
    var users = list.items.map(function(i) {return i.values().operator_user;});
    for (var i = 0; i < users.length; i++) {
        var userName = users[i];
        if (alreadyAdded.indexOf(userName) === -1) {
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
        var filters = [userNameFilter];

        var dateFilters = [
            {
                element: document.getElementById('startDateFilter'),
                comparator: function(a, b) {return a >= b;}
            },
            {
                element: document.getElementById('endDateFilter'),
                comparator: function(a, b) {return a <= b;}
            },
        ];

        for (var i = 0; i < dateFilters.length; i++) {
            var element = dateFilters[i].element;
            var comparator = dateFilters[i].comparator;
            if (element.value) {
                // closure to prevent different filters getting the same element
                filters.push((function (elementValue, comparator) {
                    return function(i) {return !i.values().operator_date || comparator( new Date(i.values().operator_date), new Date(elementValue) );};
                })(element.value, comparator));
            }
        }

        list.filter(function (i) {
            return filters.every(function(f) {return f(i);});
        });

    });
}

module.exports = {
    verify: verify,
    add: add,
    initList: initList,
    download: download
};

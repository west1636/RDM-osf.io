'use strict';

var $ = require('jquery');
var Raven = require('raven-js');
var List = require('list.js');
var $osf = require('js/osfHelpers');
var vkbeautify = require('vkbeautify');

var DOWNLOAD_FILENAME = 'timestamp_errors';
var HEADERS_ORDER = [
    'file_path', 'provider', 'version'
];
var HEADER_NAMES = {
    provider: 'Provider',
    file_id: 'File ID',
    file_path: 'File Path',
    file_name: 'File Name',
    version: 'Version'
};

var TIMESTAMP_LIST_OBJECT = new List('timestamp-form', {
    valueNames: [
        {name: 'provider', attr: 'value'},
        {name: 'file_id', attr: 'value'},
        {name: 'file_path', attr: 'value'},
        {name: 'version', attr: 'value'},
        {name: 'file_name', attr: 'value'},
        'operator_user',
        'operator_date',
    ],
});

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
            'size': fileList[i].size,
            'created': fileList[i].created,
            'modified': fileList[i].modified,
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

    var fileList = TIMESTAMP_LIST_OBJECT.items.filter(function (item) {
        var checkbox = item.elm.querySelector('[type=checkbox]');
        if (checkbox) {
            return checkbox.checked;
        }
        return false;
    }).map(function (item) {
        return item.values();
    });

    if (fileList.length === 0) {
        return false;
    }

    $('#btn-verify').attr('disabled', true);
    $('#btn-addtimestamp').attr('disabled', true);
    $('#timestamp_errors_spinner').text('Addtimestamp loading ...');
    $('#timestamp_errors_spinner').show();

    var successCount = 0;
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
            successCount++;
            $('#timestamp_errors_spinner').text('Adding Timestamp files : ' + successCount + ' / ' + fileList.length + ' ...');
            if (successCount === fileList.length) {
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
    var fileList = TIMESTAMP_LIST_OBJECT.items.filter(function (item) {
        var checkbox = item.elm.querySelector('[type=checkbox]');
        if (checkbox) {
            return checkbox.checked;
        }
        return false;
    }).map(function (item) {
        return item.values();
    });

    if (fileList.length === 0) {
        $osf.growl('Timestamp', 'Using the checkbox, please select the files to download.', 'danger');
        return false;
    }

    var fileContent;
    switch (fileFormat) {
        case 'csv':
            fileContent = generateCsv(fileList, HEADERS_ORDER, HEADER_NAMES);
            saveTextFile(DOWNLOAD_FILENAME + '.csv', fileContent);
            break;
        case 'json-ld':
            fileContent = generateJson(fileList, HEADERS_ORDER, HEADER_NAMES);
            saveTextFile(DOWNLOAD_FILENAME + '.json', fileContent);
            break;
        case 'rdf-xml':
            fileContent = vkbeautify.xml(generateXml(fileList, HEADERS_ORDER, HEADER_NAMES));
            saveTextFile(DOWNLOAD_FILENAME + '.xml', fileContent);
            break;
    }
};

function generateCsv(fileList, headersOrder, headerNames) {
    var content = '';

    // Generate header
    content += headersOrder.map(function (headerName) {
        return headerNames[headerName];
    }).join(',') + NEW_LINE;

    // Generate content
    content += fileList.map(function (file) {
        return headersOrder.map(function (headerName) {
            return file[headerName];
        }).join(',');
    }).join(NEW_LINE);

    return content;
}

function generateJson(fileList, headersOrder, headerNames) {
    // Update headers as defined in HEADERS_NAME
    fileList = fileList.map(function (file) {
        return headersOrder.reduce(function (accumulator, current) {
            accumulator[headerNames[current]] = file[current];
            return accumulator;
        }, {});
    });

    // Generate content
    return JSON.stringify(fileList, null, 2).replace(/\n/g, NEW_LINE);
}

function generateXml(fileList, headersOrder, headerNames) {
    var xml = document.implementation.createDocument(null, 'errorList');
    xml.xmlVersion = '1.0';

    var errorList = xml.getElementsByTagName('errorList')[0];

    for (var i = 0; i < fileList.length; i++) {
        var file = fileList[i];

        var fileElement = xml.createElement('file');

        for (var j = 0; j < headersOrder.length; j++) {
            var headerName = headerNames[headersOrder[j]];

            // spaces not accepted in xml tag names
            var headerElement = xml.createElement(headerName.replace(' ', ''));
            headerElement.textContent = file[headersOrder[j]];

            fileElement.appendChild(headerElement);

        }

        errorList.appendChild(fileElement);

    }

    var serializer = new XMLSerializer();
    return serializer.serializeToString(xml);
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

    var userFilterSelect = document.getElementById('userFilterSelect');

    var alreadyAdded = [''];
    var users = TIMESTAMP_LIST_OBJECT.items.map(function(i) {return i.values().operator_user;});
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
                    return function(i) {
                        // sets the time to midnight, which is the same as dates from the input fields
                        // this is needed to make items appear when the filter is set to the same day
                        var operator_date_day = new Date(i.values().operator_date);
                        operator_date_day.setHours(0, 0, 0, 0);

                        var filter_date_day = new Date(elementValue);
                        filter_date_day.setHours(0, 0, 0, 0);

                        return !i.values().operator_date || comparator( operator_date_day, filter_date_day );
                    };
                })(element.value, comparator));
            }
        }

        TIMESTAMP_LIST_OBJECT.filter(function (i) {
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

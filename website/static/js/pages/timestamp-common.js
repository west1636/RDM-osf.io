'use strict';

var $ = require('jquery');
var Raven = require('raven-js');
var List = require('list.js');
var $osf = require('js/osfHelpers');
var vkbeautify = require('vkbeautify');

var DOWNLOAD_FILENAME = 'timestamp_errors';
var HEADERS_ORDER = [
    'file_path', 'provider', 'file_version'
];
var HEADER_NAMES = {
    provider: 'Provider',
    file_id: 'File ID',
    file_path: 'File Path',
    file_version: 'Version'
};

var TIMESTAMP_LIST_OBJECT = new List('timestamp-form', {
    valueNames: [
        'provider',
        {name: 'creator_name', attr: 'value'},
        {name: 'creator_email', attr: 'value'},
        {name: 'creator_id', attr: 'value'},
        {name: 'creator_institution', attr: 'value'},
        {name: 'file_path', attr: 'value'},
        {name: 'file_id', attr: 'value'},
        {name: 'file_create_date_on_upload', attr: 'value'},
        {name: 'file_create_date_on_verify', attr: 'value'},
        {name: 'file_modify_date_on_upload', attr: 'value'},
        {name: 'file_modify_date_on_verify', attr: 'value'},
        {name: 'file_size_on_upload', attr: 'value'},
        {name: 'file_size_on_verify', attr: 'value'},
        {name: 'file_version', attr: 'value'},
        {name: 'project_id', attr: 'value'},
        {name: 'organization_id', attr: 'value'},
        {name: 'organization_name', attr: 'value'},
        {name: 'verify_user_id', attr: 'value'},
        {name: 'verify_user_name', attr: 'value'},
        {name: 'verify_date', attr: 'value'},
        {name: 'verify_result_title', attr: 'value'},
        'verify_user_name_id'
    ],
    page: 10,
    pagination: {
        paginationClass: 'listjs-pagination',
        innerWindow: 3,
        outerWindow: 1
    }
});

TIMESTAMP_LIST_OBJECT.on('updated', function (list) {
    var isFirst = list.i === 1;
    var isLast = list.i > list.matchingItems.length - list.page;

    if (list.items.length > list.page) {
        $('.pagination-wrap').show();
    } else {
        $('.pagination-wrap').hide();
    }

    $('.pagination-prev.disabled, .pagination-next.disabled').removeClass('disabled');
    if (isFirst) {
        $('.pagination-prev').addClass('disabled');
    }
    if (isLast) {
        $('.pagination-next').addClass('disabled');
    }
});

$('.pagination-prev').click(function () {
    $('.listjs-pagination .active').prev().trigger('click');
    return false;
});

$('.pagination-next').click(function () {
    $('.listjs-pagination .active').next().trigger('click');
    return false;
});

$('#pageLength').change(function () {
    TIMESTAMP_LIST_OBJECT.page = $(this).val();
    TIMESTAMP_LIST_OBJECT.update();
    $('.listjs-pagination li').first().trigger('click');
});

$('#addTimestampAllCheck').on('change', function () {
    var checkAll = this.checked;
    TIMESTAMP_LIST_OBJECT.items.map(function (item) {
        $(item.elm).find('#addTimestampCheck').prop('checked', checkAll);
    });
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
            'size': fileList[i].size,
            'created': fileList[i].created,
            'modified': fileList[i].modified,
            'file_version': fileList[i].file_version
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
            'file_version': fileList[i].file_version
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
        var fileInfo = item.values();
        var filePathArr = fileInfo.file_path.split('/');
        fileInfo.file_name = filePathArr[filePathArr.length - 1];
        return fileInfo;
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
            fileContent = generateXml(fileList, HEADERS_ORDER, HEADER_NAMES);
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
        return [
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/project/z36a9',
            '@type': 'foaf:Project',
            'rdfs:label': '"PROJ:z36a9"@en',
            'rdfs:seeAlso': {
                '@id': 'https://rdf.rdm.nii.ac.jp/z36a9'
            }
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/user/Yusuke_Komiyama',
            '@type': 'foaf:Person',
            'rdfs:label': '"Yusuke Komiyama"@en'
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/org/62615',
            '@type': 'org:Organization',
            'rdfs:label': '"ORG:62615"@en'
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/org/National_Institute_of_Informatics',
            '@type': 'frapo:organization',
            'rdfs:label': '"National Institute of Informatics"@en'
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/file/qcpxh',
            '@type': 'sio:000396',
            'dcat:bytes': 8083300.0,
            'dcterms:created': {
                '@type': 'xsd:dateTime',
                '@value': '2018-12-06_191407JST'
            },
            'dcterms:hasVersion': {
                '@type': 'xsd:int',
                '@value': '1'
            },
            'dcterms:modified': {
                '@type': 'xsd:dateTime',
                '@value': '2018-12-16_191407JST'
            },
            'dcterms:title': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/file/RCOS_leafletA3_2018.pdf'
            },
            'rdfs:label': '"FILE:qcpxh"@en',
            'rdfs:seeAlso': {
                '@id': 'https://rdf.rdm.nii.ac.jp/qcpxh'
            }
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/file/RCOS_leafletA3_2018.pdf',
            'rdfs:label': '"RCOS_leafletA3_2018.pdf"@en'
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/ts/' + file.project_id + '/' + file.file_id + '/' + file.verify_user_id + '/' + file.verify_date,
            '@type': 'dcat:Dataset',
            'dcterms:identifier': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/file/qcpxh'
            },
            'frapo:hasProjectIdentifier': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/project/z36a9'
            },
            'rdfs:label': '"TS:z36a9/qcpxh/sga29/2018-12-26_191407JST"@en',
            'sem:hasLatestEndTimeStamp': '2018-12-26_191407JST',
            'sem:hasTimestamp': 'OK',
            'sioc:id': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/user/sga29'
            }
            },
            {
            '@id': 'https://rdf.rdm.nii.ac.jp/resource/user/sga29',
            '@type': 'foaf:Agent',
            'dcterms:creator': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/user/Yusuke_Komiyama'
            },
            'org:memberOf': {
                '@id': 'https://rdf.rdm.nii.ac.jp/resource/org/62615'
            },
            'rdfs:label': '"USER:sga29"@en',
            'rdfs:seeAlso': {
                '@id': 'https://rdf.rdm.nii.ac.jp/sga29'
            },
            'vcard:hasEmail': 'komiyama@nii.ac.jp'
            }
        ];
    });

    var JSONFile = {
        '@context': {
            'dcat': 'http://www.w3.org/ns/dcat#',
            'dcterms': 'http://purl.org/dc/terms/',
            'foaf': 'http://xmlns.com/foaf/0.1/',
            'frapo': 'http://purl.org/cerif/frapo/',
            'org': 'http://www.w3.org/ns/org#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'rdmr': 'https://rdf.rdm.nii.ac.jp/resource/',
            'schema': 'http://schema.org/',
            'sem': 'http://semanticweb.cs.vu.nl/2009/11/sem/',
            'sio': 'http://semanticscience.org/resource/',
            'sioc': 'http://rdfs.org/sioc/ns#',
            'vcard': 'http://www.w3.org/2006/vcard/ns#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#'
        },
        '@graph': [fileList],
    }

    // Generate content
    return vkbeautify.json(JSON.stringify(JSONFile, null, 2));
}

function generateXml(fileList, headersOrder, headerNames) {
    var xml = document.implementation.createDocument(null, 'errorList', null);
    var errorList = xml.getElementsByTagName('errorList')[0];
    xml.xmlVersion = '1.0';

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
    return vkbeautify.xml(serializer.serializeToString(xml));
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

    // sort buttons code

    var sortFunction = function(a, b, options) {
        if (a.values().provider !== b.values().provider) {
            return TIMESTAMP_LIST_OBJECT.utils.naturalSort.caseInsensitive(a.values().provider, b.values().provider);
        }
        else {
            return TIMESTAMP_LIST_OBJECT.utils.naturalSort.caseInsensitive(a.values()[options.valueName], b.values()[options.valueName]);
        }
    };

    var propertyNames = ['provider', 'file_path', 'verify_user_name_id', 'verify_date', 'verify_result_title'];
    var clickSortUpElements = propertyNames.map(function(property_name) {
        return 'sort_up_' + property_name;
    }).map(function(click_sort_name) {
        return document.getElementById(click_sort_name);
    });

    var propertyToUpElement = {};
    propertyNames.forEach(function(propertyName, i) {
        propertyToUpElement[propertyName] = clickSortUpElements[i];
    });

    var clickSortDownElements = propertyNames.map(function(property_name) {
        return 'sort_down_' + property_name;
    }).map(function(click_sort_name) {
        return document.getElementById(click_sort_name);
    });

    var propertyToDownElement = {};
    propertyNames.forEach(function(propertyName, i) {
        propertyToDownElement[propertyName] = clickSortDownElements[i];
    });

    for (var upPropertyName in propertyToUpElement) {
        var clickSortUpElement = propertyToUpElement[upPropertyName];
        // closure to make sure propertyName is in scope at click time
        clickSortUpElement.addEventListener('click', (function(propertyName, clickSortUpElements) {
            return function(event) {

                clickSortUpElements.forEach(function(element) {
                    // written this way to ensure it works with IE
                    element.classList.add('text-muted');
                });

                clickSortDownElements.forEach(function(element) {
                    // written this way to ensure it works with IE
                    element.classList.add('text-muted');
                });

                TIMESTAMP_LIST_OBJECT.sort(propertyName, {order: 'asc', sortFunction: sortFunction});

                event.target.classList.remove('text-muted');

            };
        })(upPropertyName, clickSortUpElements));
    }

    for (var downPropertyName in propertyToDownElement) {
        var clickSortDownElement = propertyToDownElement[downPropertyName];
        // closure to make sure upPropertyName is in scope at click time
        clickSortDownElement.addEventListener('click', (function(upPropertyName, clickSortDownElements) {
            return function(event) {

                clickSortDownElements.forEach(function(element) {
                    // written this way to ensure it works with IE
                    element.classList.add('text-muted');
                });

                clickSortUpElements.forEach(function(element) {
                    // written this way to ensure it works with IE
                    element.classList.add('text-muted');
                });

                TIMESTAMP_LIST_OBJECT.sort(upPropertyName, {order: 'desc', sortFunction: sortFunction});

                event.target.classList.remove('text-muted');

            };
        })(downPropertyName, clickSortDownElements));
    }

    // filter by users and date code

    var userFilterSelect = document.getElementById('userFilterSelect');
    var alreadyAdded = [''];
    var users = TIMESTAMP_LIST_OBJECT.items.map(function(i) {return i.values().verify_user_name_id;});

    if (TIMESTAMP_LIST_OBJECT.items.length > TIMESTAMP_LIST_OBJECT.page) {
        $('.pagination-wrap').show();
    } else {
        $('.pagination-wrap').hide();
    }

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
        var userNameFilter = function(i) {return !userName || (!i.values().verify_user_name_id || (i.values().verify_user_name_id === userName));};
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
                        var verify_date_day = new Date(i.values().verify_date);
                        verify_date_day.setHours(0, 0, 0, 0);

                        var filter_date_day = new Date(elementValue);
                        filter_date_day.setHours(0, 0, 0, 0);

                        return !i.values().verify_date || comparator( verify_date_day, filter_date_day );
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

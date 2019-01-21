'use strict';

var $ = require('jquery');
var Raven = require('raven-js');
var List = require('list.js');
var $osf = require('js/osfHelpers');
var vkbeautify = require('vkbeautify');

var DOWNLOAD_FILENAME = 'timestamp_errors';
var HEADERS_ORDER = [
    'timestampId', 'fileGuidResource', 'fileGuidLabel', 'fileGuid', 'fileNameResource',
    'fileNameLabel', 'fileCreationDate', 'fileModificationDate', 'fileByteSize',
    'fileVersion', 'projectGuidResource', 'projectGuidLabel', 'projectGuid', 'userGuidResource',
    'userGuidLabel', 'userNameResource', 'userNameLabel', 'mail', 'orgIdResource', 'orgIdLabel',
    'orgNameResource', 'orgNameLabel', 'userGuid', 'tsIdLabel', 'tsVerificationStatus',
    'latestTsVerificationDate'
];
var HEADER_NAMES = {
    timestampId: 'Timestamp ID',
    fileGuidResource: 'File GUID Resource',
    fileGuidLabel: 'File GUID Label',
    fileGuid: 'File GUID',
    fileNameResource: 'File Name Resource',
    fileNameLabel: 'File Name Label',
    fileCreationDate: 'File Creation Date',
    fileModificationDate: 'File Modification Date',
    fileByteSize: 'File ByteSize',
    fileVersion: 'File Version',
    projectGuidResource: 'Project GUID Resource',
    projectGuidLabel: 'Project GUID Label',
    projectGuid: 'Project GUID',
    userGuidResource: 'User GUID Resource',
    userGuidLabel: 'User GUID Label',
    userNameResource: 'User Name Resource',
    userNameLabel: 'User Name Label',
    mail: 'Mail',
    orgIdResource: 'Organization ID Resource',
    orgIdLabel: 'Organization ID Label',
    orgNameResource: 'Organization Name Resource',
    orgNameLabel: 'Organization Name Label',
    userGuid: 'User GUID',
    tsIdLabel: 'Timestamp ID Label',
    tsVerificationStatus: 'Timestamp Verification Status',
    latestTsVerificationDate: 'Latest Timestamp Verification Date'
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
        item = item.values();

        var filePathArr = item.file_path.split('/');
        var fileName = filePathArr[filePathArr.length - 1];

        var tsDate = item.verify_date.replace(' ', '_').replace(/[/]/g, '-').replace(/:/g, '');
        var fileCreationDate = item.file_create_date_on_verify ? item.file_create_date_on_verify.replace(' ', '_').replace(/[/]/g, '-').replace(/:/g, '') : null;
        var fileModificationDate = item.file_modify_date_on_verify ? item.file_modify_date_on_verify.replace(' ', '_').replace(/[/]/g, '-').replace(/:/g, '') : null;

        return {
            timestampId: 'https://rdf.rdm.nii.ac.jp/resource/ts/' + item.project_id + '/' + item.file_id + '/' + item.verify_user_id + '/' + tsDate,
            fileGuidResource: 'https://rdf.rdm.nii.ac.jp/resource/file/' + item.file_id,
            fileGuidLabel: '"FILE:' + item.file_id + '"@en',
            fileGuid: 'https://rdf.rdm.nii.ac.jp/' + item.file_id,
            fileNameResource: 'https://rdf.rdm.nii.ac.jp/resource/file/' + fileName,
            fileNameLabel: '"' + fileName + '"@en',
            fileCreationDate: fileCreationDate,
            fileModificationDate: fileModificationDate,
            fileByteSize: item.file_size_on_verify,
            fileVersion: item.file_version,
            projectGuidResource: 'https://rdf.rdm.nii.ac.jp/resource/project/' + item.project_id,
            projectGuidLabel: '"PROJ:' + item.project_id + '"@en',
            projectGuid: 'https://rdf.rdm.nii.ac.jp/' + item.project_id,
            userGuidResource: item.creator_id ? 'https://rdf.rdm.nii.ac.jp/resource/user/' + item.creator_id : null,
            userGuidLabel: item.creator_id ? '"USER:' + item.creator_id + '"@en' : null,
            userNameResource: item.creator_name ? 'https://rdf.rdm.nii.ac.jp/resource/user/' + item.creator_name : null,
            userNameLabel: item.creator_name ? '"' + item.creator_name + '"@en' : null,
            mail: item.creator_email,
            orgIdResource: 'https://rdf.rdm.nii.ac.jp/resource/org/' + item.organization_id,
            orgIdLabel: '"ORG:' + item.organization_id + '"@en',
            orgNameResource: 'https://rdf.rdm.nii.ac.jp/resource/org/' + item.organization_name,
            orgNameLabel: '"' + item.organization_name + '"@en',
            userGuid: item.creator_id ? 'https://rdf.rdm.nii.ac.jp/' + item.creator_id : null,
            tsIdLabel: '"TS:' + item.project_id + '/' + item.file_id + '/' + item.verify_user_id + '/' + tsDate + '"@en',
            tsVerificationStatus: item.verify_result_title,
            latestTsVerificationDate: tsDate
        };
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
            fileContent = generateRdf(fileList);
            saveTextFile(DOWNLOAD_FILENAME + '.rdf', fileContent);
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
            if (file[headerName] === null) {
                return 'Unknown';
            }
            if (/["|,]/.test(file[headerName])) {
                return '"' + file[headerName].replace(/"/g, '""') + '"';
            }
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

function generateRdf (fileList) {
    var i, key;
    var doc = document.implementation.createDocument('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'rdf:RDF', null);
    doc.xmlVersion = '1.0';

    // Auxiliary functions for generating the RDF file
    var createEl = function (doc, elementName, attributes, text) {
        var element = doc.createElement(elementName);
        if (attributes) {
            var i, attr, attrName;
            for (i = 0; i < attributes.length; i++) {
                attr = attributes[i];
                for (attrName in attr) {
                    if (attr.hasOwnProperty(attrName)) {
                        element.setAttribute(attrName, attr[attrName]);
                    }
                }
            }
        }
        if (text) {
            element.textContent = text;
        }
        return element;
    };
    var linkChildren = function (element, childrenArray) {
        if (!childrenArray) {
            return;
        }
        var i, child;
        for (i = 0; i < childrenArray.length; i++) {
            child = childrenArray[i];
            linkChildren(child.element, child.children);
            element.appendChild(child.element);
        }
    };

    var namespaces = [
        {schema: 'http://schema.org/'},
        {rdmr: 'https://rdf.rdm.nii.ac.jp/resource/'},
        {owl: 'http://www.w3.org/2002/07/owl#'},
        {org: 'http://www.w3.org/ns/org#'},
        {frapo: 'http://purl.org/cerif/frapo/'},
        {xsd: 'http://www.w3.org/2001/XMLSchema#'},
        {rdfs: 'http://www.w3.org/2000/01/rdf-schema#'},
        {vcard: 'http://www.w3.org/2006/vcard/ns#'},
        {rdf: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
        {sio: 'http://semanticscience.org/resource/'},
        {dcterms: 'http://purl.org/dc/terms/'},
        {sem: 'http://semanticweb.cs.vu.nl/2009/11/sem/'},
        {dcat: 'http://www.w3.org/ns/dcat#'},
        {foaf: 'http://xmlns.com/foaf/0.1/'},
        {sioc: 'http://rdfs.org/sioc/ns#'},
    ];

    // Add namespaces to root (rdf)
    for (i = 0; i < namespaces.length; i++) {
        for (key in namespaces[i]) {
            if (namespaces[i].hasOwnProperty(key)) {
                doc.documentElement.setAttribute('xmlns:' + key, namespaces[i][key]);
            }
        }
    }

    for (i = 0; i < fileList.length; i++) {
        var item = fileList[i];

        var rdfElements = [
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.timestampId}]),
                children: [
                    {element: createEl(doc, 'rdf:type', [{'rdf:resource': 'http://www.w3.org/ns/dcat#Dataset'}])}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.fileGuidResource}]),
                children: [
                    {element: createEl(doc, 'rdf:type', [{'rdf:resource': 'http://semanticscience.org/resource/SIO_000396'}])},
                    {element: createEl(doc, 'rdfs:seeAlso', [{'rdf:resource': item.fileGuid}])},
                    {element: createEl(doc, 'rdfs:label', null, item.fileGuidLabel)}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.fileNameResource}]),
                children: [
                    {element: createEl(doc, 'rdfs:label', null, item.fileNameLabel)}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.fileGuidResource}]),
                children: [
                    {element: createEl(doc, 'dcterms:title', [{'rdf:resource': item.fileNameResource}])},
                    {element: createEl(doc, 'dcterms:created', [{'rdf:datatype': 'http://www.w3.org/2001/XMLSchema#dateTime'}], item.fileCreationDate ? item.fileCreationDate : 'Unknown')},
                    {element: createEl(doc, 'dcterms:modified', [{'rdf:datatype': 'http://www.w3.org/2001/XMLSchema#dateTime'}], item.fileModificationDate ? item.fileModificationDate : 'Unknown')},
                    {element: createEl(doc, 'dcat:bytes', [{'rdf:datatype': 'http://www.w3.org/2001/XMLSchema#double'}], item.fileByteSize ? item.fileByteSize : 'Unknown')},
                    {element: createEl(doc, 'dcterms:hasVersion', [{'rdf:datatype': 'http://www.w3.org/2001/XMLSchema#int'}], item.fileVersion ? item.fileVersion : 'Unknown')}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.timestampId}]),
                children: [
                    {element: createEl(doc, 'dcterms:identifier', [{'rdf:resource': item.fileGuidResource}])}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.projectGuidResource}]),
                children: [
                    {element: createEl(doc, 'rdf:type', [{'rdf:resource': 'http://xmlns.com/foaf/0.1/Project'}])},
                    {element: createEl(doc, 'rdfs:seeAlso', [{'rdf:resource': item.projectGuid}])},
                    {element: createEl(doc, 'rdfs:label', null, item.projectGuidLabel)}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.timestampId}]),
                children: [
                    {element: createEl(doc, 'frapo:hasProjectIdentifier', [{'rdf:resource': item.projectGuidResource}])}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.userGuidResource ? item.userGuidResource : 'Unknown'}]),
                children: [
                    {element: createEl(doc, 'rdf:type', [{'rdf:resource': 'http://xmlns.com/foaf/0.1/Agent'}])},
                    {element: createEl(doc, 'rdfs:label', null, item.userGuidLabel ? item.userGuidLabel : 'Unknown')}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.userNameResource ? item.userNameResource : 'Unknown'}]),
                children: [
                    {element: createEl(doc, 'rdf:type', [{'rdf:resource': 'http://xmlns.com/foaf/0.1/Person'}])},
                    {element: createEl(doc, 'rdfs:label', null, item.userNameLabel ? item.userNameLabel : 'Unknown')}
                ]
            },
            {
                element: createEl(doc, 'rdf:Description', [{'rdf:about': item.userGuidResource ? item.userGuidResource : 'Unknown'}]),
                children: [
                    {element: createEl(doc, 'dcterms:creator', [{'rdf:resource': item.userNameResource ? item.userNameResource : 'Unknown'}])},
                    {element: createEl(doc, 'vcard:hasEmail', null, item.mail ? item.mail : 'Unknown')}
                ]
            }
        ];

        linkChildren(doc.documentElement, rdfElements);
    }

    var serializer = new XMLSerializer();
    return vkbeautify.xml(serializer.serializeToString(doc)).replace(/\n/g, NEW_LINE);
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

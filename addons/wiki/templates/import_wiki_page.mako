<!-- New Component Modal -->
<div class="modal fade" id="importWiki">
    <div class="modal-dialog">
        <div class="modal-content">
            <form class="form">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h3 class="modal-title">${_("Import wiki page")}</h3>
                </div><!-- end modal-header -->
                <div class="modal-body">
                    <div class='form-group'>
                        <select id="importDir" class="form-control">
                            % for import_dir in import_dirs:
                                <option value="${import_dir['id']}">${import_dir['name']}</option>
                            % endfor
                        </select>
                    </div>
                </div><!-- end modal-body -->
                <div class="modal-footer">
                    <a id="close" href="#" class="btn btn-default" data-dismiss="modal">${_("Cancel")}</a>
                    <button id="importWikiSubmit" type="submit" class="btn btn-success">${_("Import")}</button>
                </div><!-- end modal-footer -->
            </form>
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<div class="modal fade" id="alertInfo">
    <div class="modal-dialog">
        <div class="modal-content">
            <form class="form">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h3 class="modal-title">${_("Duplicate wiki name")}</h3>
                </div><!-- end modal-header -->
                <div class="modal-body">
                    <p id="attentionValidateInfo" style="display: none">
                        ${_('The following wiki page already exists. Please select the process when importing. When creating a new wiki, the wiki name will be created with a sequential number like [Wiki name](1). If you dismiss this alert, the import will be aborted.')}
                    </p>
                    <div class="partOperationAll">
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="skipAll" value="skipAll" checked /><label for="skipAll">Skip All</label></div>
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="overwriteAll" value="overwriteAll"/><label for="overwriteAll">Overwrite All</label></div>
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="createNewAll" value="createNewAll"/><label for="createNewAll">Create New All</label></div><br>
                    </div>
                    <div id="validateInfo" class="partOperationAll">
                        <ul></ul>
                    </div>
                    <p id="attentionDuplicatedInfo" style="display: none" class="partOperationAll">
                        ${_('Duplicate wiki page name. The following pages will be registered as the Wiki page name listed.')}
                    </p>
                    <div id="duplicatedInfo" class="partOperationAll">
                        <ul></ul>
                    </div>
                    <div id="perFileDifinitionForm" style="display: none">
                        <ul></ul>
                    </div>
                    <p id="attentionDuplicatedFolder" style="display: none">
                        ${_('The following folder are duplicated in the import directory.')}
                    </p>
                    <div id="duplicatedFolder">
                        <ul></ul>
                    </div>
                </div><!-- end modal-body -->
                <div class="modal-footer">
                    <a id="stopImport" href="#" class="btn btn-default btnAll" data-dismiss="modal" style="display: none">${_("Stop import")}</a>
                    <button id="backalertInfo" type="button" class="btn btn-default btnIndividual" style="display: none">${_("Back")}</button>
                    <button id="continueImportWikiSubmit" type="submit" class="btn btn-success btnAll btnIndividual" style="display: none">${_("Continue import")}</button>
                    <button id="perFileDefinition" type="button" class="btn btn-warning btnAll" style="display: none">${_("Per-file definition")}</button>
                </div><!-- end modal-footer -->
            </form>
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<div class="modal fade" id="importResult">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h3 class="modal-title">${_("Import Result")}</h3>
            </div><!-- end modal-header -->
            <div class="modal-body">
                <p id="importComplete" style="display: none">
                    ${_("Import Complete.")}
                </p>
            </div><!-- end modal-body -->
            <div class="modal-footer">
                <a href="#" class="btn btn-default" data-dismiss="modal" style="display: none">${_("OK")}</a>
            </div><!-- end modal-footer -->
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<script type="text/javascript">
    $(function () {
        var $importWikiForm = $('#importWiki form');
        var $alertInfoForm = $('#alertInfo form');
        var selectOperation = '<div class="form-group importOperationPer" style="display: inline-block; margin-left: 10px;"><select class="form-control"><option value="skip">Skip</option><option value="overwirte">Overwrite</option><option value="createNew">Create New</option></select></div>'
        var validateResult = {};
        var promisesWB = [];
        var promisesRootImportProcess = [];
        var promisesSubordinateImportProcess = [];
        var imageFolder = 'Wiki images';
        var importFolder = 'Imported Wiki workspace (temporary)';
        $importWikiForm.on('submit', function (e) {
            e.preventDefault();

            var $importDir = $importWikiForm.find('#importDir');
            var $submitForm = $importWikiForm.find('#importWikiSubmit');

            $submitForm
                .attr('disabled', 'disabled')
                .text('${_("Importing wiki pages")}');

                // TODO: helper to eliminate slashes in the url.
                var dirId = $importDir.val();
                var importUrl = ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/validate/';
                var request = $.ajax({
                    type: 'GET',
                    cache: false,
                    url: importUrl,
                    dataType: 'json'
                });
                request.done(function (response) {
                    $submitForm
                        .removeAttr('disabled', 'disabled')
                        .text('${_("Import")}');
                    console.log(response.canStartImport)
                    if (response.canStartImport) {
                        startImportWiki(response, dirId, $submitForm);
                    } else {
                        $('#alertInfo').modal('show');
                        $('#importWiki').modal('hide');
                        console.log(response.duplicated_folder)
                        if (response.duplicated_folder.length > 0) {
                            $('#attentionDuplicatedFolder').css('display', '');
                            $alertInfoForm.find('.partOperationAll').css('display', 'none');
                            $('#backalertInfo').css('display', '');
                            response.duplicated_folder.forEach(function(item) {
                                $('#duplicatedFolder ul').append('<li>' + item + '</li>');
                            });
                        } else {
                            validateResult = response.data;
                            $('.btnAll').css('display', '');
                            response.data.forEach(function(item) {
                                if (item.status === 'valid_exists') {
                                    $('#attentionValidateInfo').css('display', '');
                                    $('#validateInfo ul').append('<li>' + (item.path).slice(1) + '</li>')
                                    $('#perFileDifinitionForm ul').append('<li id="' + (item.path).slice(1) + '">' + '<div style="display: inline-block">' +  (item.path).slice(1) + '</div>' + selectOperation + '</li>')
                                } else if (item.status === 'valid_duplicated'){
                                    $('#attentionDuplicatedInfo').css('display', '');
                                    $('#duplicatedInfo ul').append('<li>' + (item.path).slice(1) + '</li>')
                                }
                            });
                        }
                    }
                });
                request.fail(function (response, textStatus, error) {
                    $alert.text('${_("Could not validate wiki page. Please try again.")}'+response.status);
                    Raven.captureMessage('${_("Error occurred while validating page")}', {
                        extra: {
                            url: ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/validate/',
                            textStatus: textStatus,
                            error: error
                        }
                    });
                    $submitForm
                        .removeAttr('disabled', 'disabled')
                        .text('${_("Import")}');
                });
        });

        $alertInfoForm.on('submit', function (e) {
            e.preventDefault();
            console.log('---continue import---')
            var $importDir = $importWikiForm.find('#importDir');
            var $submitForm = $alertInfoForm.find('#continueImportWikiSubmit');
            var operationAll = '';
            var perFileList = []
            var perFileDifinitionFormDisplay = document.getElementById('perFileDifinitionForm').style.display;

            if (perFileDifinitionFormDisplay === 'none') {
                var importOperations = document.getElementsByName('importOperation');
                for (var i = 0; i < importOperations.length; i++){
                    if (importOperations.item(i).checked) {
                        operationAll = importOperations.item(i).value;
                    }
                }
            } else if (perFileDifinitionFormDisplay === '') {
                console.log('---create perfileoperationlist---');
                var $perFileList = $('#perFileDifinitionForm li');
                for (var i = 0; i < $perFileList.length; i++){
                    for (var j = 0; j < $perFileList[i].children.length; j++){
                        if ($perFileList[i].children[j].classList.length !== 0) {
                            perFileList.push({path: $perFileList[i].id, operation: $perFileList[i].children[j].firstChild.value});
                        }
                    }
                }
            }
            $submitForm
                .attr('disabled', 'disabled')
                .text('${_("Importing wiki pages")}');

                // TODO: helper to eliminate slashes in the url.
                var dirId = $importDir.val();
                var importUrl = ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/';
                console.log(importUrl)
                $('#alertInfo').modal('hide');
                var request = $.ajax({
                    type: 'POST',
                    cache: false,
                    url: importUrl,
                    data: JSON.stringify({dirId: dirId, operationAll: operationAll, perFileList: perFileList, validateResult: validateResult}),
                    dataType: 'json'
                });
                request.done(function (response) {
                    $submitForm
                        .removeAttr('disabled', 'disabled')
                        .text('${_("Import")}');
                    console.log('import complete')
                });
                request.fail(function (response, textStatus, error) {
                    $alert.text('${_("Could not validate wiki page. Please try again.")}'+response.status);
                    Raven.captureMessage('${_("Error occurred while validating page")}', {
                        extra: {
                            url: ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/validate/',
                            textStatus: textStatus,
                            error: error
                        }
                    });
                    $submitForm
                        .removeAttr('disabled', 'disabled')
                        .text('${_("Import")}');
                });
        });

        $alertInfoForm.find('#perFileDefinition').on('click', function () {
            showPerFileDefinition();
        });
        $alertInfoForm.find('#backalertInfo').on('click', function () {
            backalertInfo();
        });
        $('#alertInfo').on('hidden.bs.modal', function (event) {
            $('#alertInfo li').remove();
        });

        function showPerFileDefinition() {
            $alertInfoForm.find('.partOperationAll').css('display', 'none');
            $alertInfoForm.find('.btnAll').css('display', 'none');
            $alertInfoForm.find('.btnIndividual').css('display', '');
            $alertInfoForm.find('#perFileDifinitionForm').css('display', '');
        }
        function backalertInfo() {
            $alertInfoForm.find('.partOperationAll').css('display', '');
            $alertInfoForm.find('#perFileDifinitionForm').css('display', 'none');
            $alertInfoForm.find('.btnIndividual').css('display', 'none');
            $alertInfoForm.find('.btnAll').css('display', '');
        }
        function startImportWiki(res, dirId, $submitForm) {
            console.log('7777 will start')
            var readingCtn = 0;
            var totalCtn = (res.data).length
            $submitForm.attr('disabled', 'disabled').text('${_("Reading Wiki Contents")}' + readingCtn + '/' + totalCtn);
            console.log(res.data);
//            var mfr_format_url = "http://localhost:7777/v1/resources/{1}/providers/osfstorage/{2}?direct=true&mode=render"
            var mfr_format_url = window.contextVars.waterbutlerURL  + 'v1/resources/{1}/providers/osfstorage/{2}?direct=true&mode=render'
            var wiki_info = []
            console.log(res.data)
            for (var i = 0; i < res.data.length; i++) {
                var fileName = res.data[i].name;
                var ext = /(?:\.([^.]+))?$/.exec(fileName)[1];
                if (ext !== 'md') {
                    continue;
                }
                var parentWikiName = res.data[i].parent_wiki_name;
                var mfr_url = mfr_format_url.replace('{1}', window.contextVars.node.id).replace('{2}', res.data[i]._id);
                promisesWB.push(
                    $.ajax({
                        type: 'GET',
                        url: mfr_url,
                        dataType: 'text',
                        beforeSend: function (xhr, options) {
                            if (navigator.appVersion.indexOf('MSIE 9.') === -1) {
                                xhr.withCredentials = true;
                                xhr.fileName = fileName;
                                xhr.parentWikiName = parentWikiName;
                                xhr.path = res.data[i].path;
                                xhr.validation = res.data[i].status;
                                if (options) {
                                    options.withCredentials = true;
                                    options.xhrFields = {withCredentials:true};
                                }
                            }
                            return xhr;
                        }
                    }).done(function (parsed, status, response) {
                        console.log('success is ' + response.fileName)
                        readingCtn = readingCtn + 1;
                        console.log(readingCtn)
                        $submitForm.attr('disabled', 'disabled').text('${_("Reading Wiki Contents")}' + readingCtn + '/' + totalCtn);
                        wiki_info.push({path: response.path, wiki_name: response.fileName, wiki_content: response.responseText, parent_wiki_name: response.parentWikiName, validation: response.validation});
                    }).fail(function (response) {
                        console.log(response);
                        console.log('error is '  + response.fileName)
                    })
                );
            }
            $.when.apply(null, promisesWB).done(function () {
                console.log('7777 end')
                var copyImportDirectryUrl = ${ urls['api']['base'] | sjson, n } + 'copy_import_directory/' + dirId + '/';
                $submitForm.attr('disabled', 'disabled').text('${_("Copying Wiki Import Directory")}');
                getOrCreateWikiImagesFolder(imageFolder).fail(function(response) {
                    console.log('failed to create wiki imagess')
                }).done(function(path) {
                    var copyRequest = $.ajax({
                        type: 'POST',
                        cache: false,
                        url: copyImportDirectryUrl,
                        data: JSON.stringify({ validationResult: res.data, folderPath: path}),
                        contentType: 'application/json; charset=utf-8',
                    });
                    copyRequest.done(function (response) {
                        console.log(wiki_info);
                        console.log(response.clonedId);
                        $submitForm.attr('disabled', 'disabled').text('${_("Import Preparing")}');
//                        return;
                        var replaceUrl = ${ urls['api']['base'] | sjson, n } + 'replace/' + response.clonedId + '/';
                        var request = $.ajax({
                            type: 'POST',
                            url: replaceUrl,
                            data: JSON.stringify({ wiki_info: wiki_info}),
                            contentType: 'application/json; charset=utf-8',
                        }).done(function (response) {
                            console.log('---replace done---')
                            var importCtn = 0;
                            var wiki_info = response.replaced;
                            var totalCtn = wiki_info.length;
                            $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki Page")}' + importCtn + '/' + totalCtn);
                            console.log(wiki_info);
                            for (var i = 0; i < wiki_info.length; i++) {
                                var importProcessUrl = ${ urls['api']['base'] | sjson, n } + encodeURIComponent(wiki_info[i].wiki_name) + '/import_process/';
                                if (wiki_info[i].parent_wiki_name === null) {
                                    promisesRootImportProcess.push(
                                        $.ajax({
                                            type: 'POST',
                                            cache: false,
                                            url: importProcessUrl,
                                            data: wiki_info[i].wiki_content,
                                            contentType: 'json'
                                        }).done(function (response) {
                                            importCtn = importCtn + 1;
                                            $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki Page")}' + importCtn + '/' + totalCtn);
                                            console.log('---wiki create or update---')
                                        }).fail(function (response) {
                                            console.log(response);
                                            alert('error2');
                                        })
                                    );
                                }
                            }
                            $.when.apply(null, promisesRootImportProcess).done(function () {
                                console.log('---root wiki page created done---')
                                // subordinate wiki pages is created.
                                console.log(wiki_info);
                                importSameLevelWiki(wiki_info, 1, $submitForm, importCtn, totalCtn);
                            });
                        });
                    });
                });
            });
        }
        function importSameLevelWiki(wiki_info, depth, $submitForm, importCtn, totalCtn) {
            console.log('---importsamelevelwiki---')
            var complete = true;
            var maxDepth = getMaxDepth(wiki_info);
            console.log(wiki_info)
            if (depth > maxDepth) {
                const reloadUrl = (location.href).replace(location.search, '')
                window.location.assign(reloadUrl);
                return;
            }
            var promisesSubordinateImportProcess = [];
            for (var i = 0; i < wiki_info.length; i++) {
                var slashCnt = ( (wiki_info[i].path).match( /\//g ) || [] ).length ;
                var wiki_depth = slashCnt - 1;
                if (depth === wiki_depth) {
                    complete = false;
                    var importProcessUrl = ${ urls['api']['base'] | sjson, n } + encodeURIComponent(wiki_info[i].wiki_name) + '/parent/' + encodeURIComponent(wiki_info[i].parent_wiki_name) + '/import_process/';
                    /*
                    var dfd = new $.Deferred();
                    $.ajax({
                        type: 'POST',
                        cache: false,
                        url: importProcessUrl,
                        data: wiki_info[i].wiki_content,
                        contentType: 'json'
                    }).done(function (response) {
                        importCtn = importCtn + 1;
                        $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki Page")}' + importCtn + '/' + totalCtn);
                    }).fail(function (response) {
                        console.log('error3')
                    }).always( function (response) {
                        console.log('always')
                        dfd.resolve();
                    })
                    promisesSubordinateImportProcess.push(dfd.promise());
//                    alert('ajax')
                    */
                    promisesSubordinateImportProcess.push(
                        $.ajax({
                            type: 'POST',
                            cache: false,
                            url: importProcessUrl,
                            data: wiki_info[i].wiki_content,
                            contentType: 'json'
                        }).done(function (response) {
                            importCtn = importCtn + 1;
                            console.log('aaa')
                            $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki Page")}' + importCtn + '/' + totalCtn);
                            console.log('bbb')
                        }).fail(function (response) {
                            console.log('error3')
                        }).always( function (response) {
                            console.log('always');
                        })
                    );
                    /*
                    promisesSubordinateImportProcess.push(
                        $.ajax({
                            type: 'POST',
                            cache: false,
                            url: importProcessUrl,
                            data: wiki_info[i].wiki_content,
                            contentType: 'json'
                        }).done(function (response) {
                            importCtn = importCtn + 1;
                            $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki Page")}' + importCtn + '/' + totalCtn);
                            console.log('---wiki create or update---')
                        }).fail(function (response) {
                            console.log(response);
                            console.log('error3:::')
                        })
                    );
                    */
                }
            }
            $.when.apply($, promisesSubordinateImportProcess).done(function () {
                if (!complete) {
                    importSameLevelWiki(wiki_info, depth + 1, $submitForm, importCtn, totalCtn);
                }
            });
        }
        function getMaxDepth(wiki_info) {
            var max = 0;
            for (var i = 0; i < wiki_info.length; i++) {
                var now = ( (wiki_info[i].path).match( /\//g ) || [] ).length ;
                if (now > max) {
                    max=now
                }
            }
            return max - 1;
        }
        /**
         * Override from wikiPage.js
         */
        function createSubFolder(newFolderLink, folderName) {
            return $.ajax({
                url: newFolderLink + '&name=' + encodeURI(folderName),
                type: 'PUT',
                beforeSend: function (xhr, options) {
                    if (navigator.appVersion.indexOf('MSIE 9.') === -1) {
                        xhr.withCredentials = true;
                        if (options) {
                            options.withCredentials = true;
                            options.xhrFields = {withCredentials:true};
                        }
                    }
                    return xhr;
                }
            });
        };
        function getOrCreateWikiImportFolder(imageFolder, dir_id) {
            var folderUrl = ${ urls['api']['base'] | sjson, n } + 'get_imported_wiki_workspace/' + dir_id + '/';
            console.log(folderUrl)
            return $.ajax({
                url: folderUrl,
                type: 'POST',
                dataType: 'json'
            }).then(function(response) {
                console.log(response)
                var link = window.contextVars.waterbutlerURL + 'v1/resources/' + window.contextVars.node.id + '/providers/osfstorage' + response.path + '?kind=folder';
                if (response.exist) {
                    console.log('import folder is existed.')
                    return createSubFolder(link, Math.random().toString(32).substring(2)).then(function(response) {
                        return response.data.attributes.path;
                    });
                } else {
                    console.log('import folder is not existed')
                    return createSubFolder(link, importFolder).then(function(response) {
                        return createSubFolder(response.data.links.new_folder, Math.random().toString(32).substring(2)).then(function(response) {
                            return response.data.attributes.path;
                        });
                    });
                }
            });
        };
        /**
         * Override from wikiPage.js
         */
        function createFolder() {
            return $.ajax({
                url: window.contextVars.waterbutlerURL + 'v1/resources/' + window.contextVars.node.id + '/providers/osfstorage/?name=' + encodeURI(imageFolder) + '&kind=folder',
                type: 'PUT',
                beforeSend: function (xhr, options) {
                    if (navigator.appVersion.indexOf('MSIE 9.') === -1) {
                        xhr.withCredentials = true;
                        if (options) {
                            options.withCredentials = true;
                            options.xhrFields = {withCredentials:true};
                        }
                    }
                    return xhr;
                }
            });
        };
        /**
         * Override from wikiPage.js
         */
        function getOrCreateWikiImagesFolder(imageFolder) {
            var folderUrl = window.contextVars.apiV2Prefix + 'nodes/' + window.contextVars.node.id + '/files/osfstorage/?filter[kind]=folder&fields[file]=name,path&filter[name]=' + encodeURI(imageFolder);
            console.log(folderUrl)
            return $.ajax({
                url: folderUrl,
                type: 'GET',
                dataType: 'json',
                beforeSend: function (xhr, options) {
                    if (navigator.appVersion.indexOf('MSIE 9.') === -1) {
                        xhr.withCredentials = true;
                        if (options) {
                            options.withCredentials = true;
                            options.xhrFields = {withCredentials:true};
                        }
                    }
                    return xhr;
                }
            }).then(function(response) {
                if (response.data.length > 0) {
                    console.log('wiki images is existed.')
                    for (var i = 0, folder; folder = response.data[i]; i++) {
                        var name = folder.attributes.name;
                        var id = folder.id;
                        if (name === imageFolder) {
                            console.log(folder);
                            return getOrCreateWikiImportFolder(importFolder, id);
                        }
                    }
                }
                if (response.data.length === 0) {
                    console.log('wiki images is not existed')
                    return createFolder(imageFolder).then(function(response) {
                        console.log(response.data)
                        return createSubFolder(response.data.links.new_folder, importFolder).then(function(response) {
                            return createSubFolder(response.data.links.new_folder, Math.random().toString(32).substring(2)).then(function(response) {
                                return response.data.attributes.path;
                            });
                        });
                    });
                }
            });
        };
    });
</script>

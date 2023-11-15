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
                <div id="importFooter" class="modal-footer">
                    <a id="closeImport" href="#" class="btn btn-default" data-dismiss="modal">${_("Close")}</a>
                    <button class="stopImport btn btn-default" href="#" class="btn btn-default" data-dismiss="modal" style="display: none">${_("Stop import")}</button>
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
                <div class="modal-body" style="height: 550px;overflow: auto;">
                    <p id="attentionValidateInfo" class="partOperationAll" style="display: none">
                        ${_('The following wiki page already exists. Please select the process when importing. When creating a new wiki, the wiki name will be created with a sequential number like [Wiki name](1). If you dismiss this alert, the import will be aborted.')}
                    </p>
                    <div class="partOperationAll" style="display: none">
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="skipAll" value="skipAll" checked /><label for="skipAll">Skip All</label></div>
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="overwriteAll" value="overwriteAll"/><label for="overwriteAll">Overwrite All</label></div>
                      <div style="display: inline-block; margin-right: 10px;"><input name="importOperation" type="radio" id="createNewAll" value="createNewAll"/><label for="createNewAll">Create New All</label></div><br>
                    </div>
                    <div id="validateInfo" class="partOperationAll">
                        <ul></ul>
                    </div>
                    <p id="attentionDuplicatedInfo" style="display: none">
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
                    <button class="stopImport btn btn-default" href="#" class="btn btn-default" data-dismiss="modal" style="display: none">${_("Stop import")}</button>
                    <button id="backalertInfo" type="button" class="btn btn-default btnIndividual" style="display: none">${_("Back")}</button>
                    <button id="closeAlertInfo" type="button" class="btn btn-default" data-dismiss="modal" style="display: none">${_("Close")}</button>
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
                <div id="showImportError" style="display: none">
                </div>
            </div><!-- end modal-body -->
            <div class="modal-footer">
                <a href="#" class="btn btn-success" data-dismiss="modal" >${_("OK")}</a>
            </div><!-- end modal-footer -->
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<script type="text/javascript">
    $(function () {
        var $importWikiForm = $('#importWiki form');
        var $alertInfoForm = $('#alertInfo form');
        var $importResult = $('#importResult')
        var selectOperation = '<div class="form-group" name="importOperationPer" style="display: inline-block; margin-left: 10px;"><select class="form-control" name="importOperationPerSelect"><option value="skip">Skip</option><option value="overwrite">Overwrite</option><option value="createNew">Create New</option></select></div>'
        var validationResult = [];
        var wiki_info = []
        var importErrors = [];
        var importCtn = 0;
        var readingCtn = 0;
        var imageFolder = 'Wiki images';
        var importFolder = 'Imported Wiki workspace (temporary)';
        const VALIDATE_IMPORT_TIMEOUT = 60;
        const WIKI_IMPORT_TIMEOUT = 600;
        var celeryTask = {
            _id: 0,
            get id() {
                return this._age;
            },
            set id(val) {
                this._id = val;
            }
        };

        $importWikiForm.on('submit', function (e) {
            e.preventDefault();
            var $importDir = $importWikiForm.find('#importDir');
            var $submitForm = $importWikiForm.find('#importWikiSubmit');
            var $stopImport = $importWikiForm.find('.stopImport');

            $submitForm
                .attr('disabled', 'disabled')
                .text('${_("Validating wiki pages")}');

                // TODO: helper to eliminate slashes in the url.
                var dirId = $importDir.val();
                var validateImportUrl = ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/validate/';
                console.log('---validate start---')
                var request = $.ajax({
                    type: 'GET',
                    cache: false,
                    url: validateImportUrl,
                    dataType: 'json'
                }).done(async function (response) {
                    console.log('---validate task---')
                    var taskId = response.taskId;
                    var getTaskResultUrl = ${ urls['api']['base'] | sjson, n } + 'get_task_result/' + taskId+ '/';
                    console.log(taskId);
                    var validateImportResult = await intervalGetCeleryTaskResult(getTaskResultUrl, 1000, VALIDATE_IMPORT_TIMEOUT, 'validate wiki pages')
                    if (!validateImportResult) {
                        return;
                    }
                    $submitForm.removeAttr('disabled', 'disabled').text('${_("Import")}');
                    if (validateImportResult.canStartImport) {
                        var data = fixToImportList('', validateImportResult.data)
                        // hide Close Btn
                        $importWikiForm.find('#closeImport').css('display', 'none');
                        startImportWiki(data, dirId, $submitForm, $stopImport);
                    } else {
                        $('#alertInfo').modal('show');
                        $('#importWiki').modal('hide');
                        if (validateImportResult.duplicated_folder.length > 0) {
                            // show duplicated folder sentence
                            $('#attentionDuplicatedFolder').css('display', '');
                            // show Close Btn
                            $('#closeAlertInfo').css('display', '');
                            // hide the display of operations for all
                            $alertInfoForm.find('.partOperationAll').css('display', 'none');
                            // show duplicated import folder list
                            validateImportResult.duplicated_folder.forEach(function(item) {
                                $('#duplicatedFolder ul').append('<li>' + item + '</li>');
                            });
                        } else {
                            validationResult = validateImportResult.data;
                            // show the Btn of operations for all
                            $('.btnAll').css('display', '');
                            // show duplicated wiki page infomation
                            validationResult.forEach(function(item) {
                                if (item.status === 'valid_exists') {
                                    $alertInfoForm.find('.partOperationAll').css('display', '');
                                    $('#validateInfo ul').append('<li>' + (item.path).slice(1) + '</li>')
                                    $('#perFileDifinitionForm ul').append('<li id="' + (item.path).slice(1) + '" style="display: flex;justify-content: flex-end;">' + '<div style="display: list-item; position: absolute; left: 55px; max-width: 410px;">' +  (item.path).slice(1) + '</div>' + selectOperation + '</li>');
                                } else if (item.status === 'valid_duplicated'){
                                    $('#attentionDuplicatedInfo').css('display', '');
                                    $('#duplicatedInfo ul').append('<li>' + (item.path).slice(1) + '</li>')
                                }
                            });
                        }
                    }
                }).fail(function (response, textStatus, error) {
                    $alertInfoForm.text('${_("Could not validate wiki page. Please try again.")}'+response.status);
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
            var $importDir = $importWikiForm.find('#importDir');
            var $submitForm = $alertInfoForm.find('#continueImportWikiSubmit');
            var $perFile = $alertInfoForm.find('#perFileDefinition');
            var $perBack = $alertInfoForm.find('#backalertInfo');
            var $stopImport = $alertInfoForm.find('.stopImport');
            var operationAll = null;
            var perOperationList = []
            var perFileDifinitionFormDisplay = document.getElementById('perFileDifinitionForm').style.display;

            if (perFileDifinitionFormDisplay === 'none') {
                var importOperations = document.getElementsByName('importOperation');
                for (var i = 0; i < importOperations.length; i++){
                    if (importOperations.item(i).checked) {
                        operationAll = importOperations.item(i).value;
                    }
                }
            } else if (perFileDifinitionFormDisplay === '') {
                var $perFileList = $('#perFileDifinitionForm li');
                for (var j = 0; j < $perFileList.length; j++){
                    var wiki_name = ($perFileList[j].id).substring(($perFileList[j].id).lastIndexOf('/') + 1);
                    var operation = $perFileList[j].children.importOperationPer.children.importOperationPerSelect.value;
                    var opList = { wiki_name: wiki_name, operation: operation};
                    perOperationList.push(opList);
                }
            }
            var validationResultCopy = validationResult.slice();
            var validationResultFix = fixToImportList(operationAll, validationResultCopy, perOperationList);
            if (validationResultFix.length === 0) {
                alert('No page to import.');
                return;
            }
            // TODO: helper to eliminate slashes in the url.
            var dirId = $importDir.val();
            $perFile.attr('disabled', 'disabled');
            $perBack.attr('disabled', 'disabled');
            startImportWiki(validationResultFix, dirId, $submitForm, $stopImport);
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
        $alertInfoForm.find('.stopImport').on('click', function () {
            var $submitForm = $alertInfoForm.find('#continueImportWikiSubmit');
            $submitForm.attr('disabled', 'disabled').text('${_("Aborting Import Wiki...")}');
            abortCeleryTask(celeryTask.id)
            return;
        });
        $importWikiForm.find('.stopImport').on('click', function () {
            var $submitForm = $importWikiForm.find('#importWikiSubmit');
            $submitForm.attr('disabled', 'disabled').text('${_("Aborting Import Wiki...")}');
            abortCeleryTask(celeryTask.id)
            return;
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

        async function startImportWiki(data, dirId, $submitForm, $stopImport) {
            readingCtn = 0;
            var totalCtn = (data).length
            $submitForm.attr('disabled', 'disabled').text('${_("Reading Wiki Contents")}' + readingCtn + '/' + totalCtn);
            var mfr_format_url = window.contextVars.waterbutlerURL  + 'v1/resources/{1}/providers/osfstorage/{2}?direct=true&mode=render'
            wiki_info = []
            // Get Markdown content
            for (var i = 0; i < data.length; i++) {
                if (data[i]._id === undefined) {
                    continue;
                }
                var mfr_url = mfr_format_url.replace('{1}', window.contextVars.node.id).replace('{2}', data[i]._id);
                try {
                    await getMdContentFromWB(mfr_url, data[i], $submitForm, totalCtn);
                } catch(e) {
                    console.log('failed to get md content: ' + data[i].name)
                }
            }
            // Wiki images, Imported Wiki workspace and copy wiki miport directoy
            var wikiImportUrl = ${ urls['api']['base'] | sjson, n } + 'import/' + dirId + '/';
            $submitForm.attr('disabled', 'disabled').text('${_("Creating Wiki Folder...")}');
            getOrCreateWikiImagesFolder(imageFolder).fail(function(response) {
                if (response.status !== 0) {
                    alert('failed to get or create wiki folder')
                    const reloadUrl = (location.href).replace(location.search, '')
                    window.location.assign(reloadUrl);
                }
            }).done(function(path) {
                // show stop import Btn
                $stopImport.css('display', '');
                $submitForm.attr('disabled', 'disabled').text('${_("Importing Wiki...")}');
                $.ajax({
                    type: 'POST',
                    cache: false,
                    url: wikiImportUrl,
                    data: JSON.stringify({folderPath: path, wiki_info: wiki_info}),
                    contentType: 'application/json; charset=utf-8',
                }).done(async function (response) {
                    var taskId = response.taskId;
                    celeryTask._id = taskId;
                    var getTaskResultUrl = ${ urls['api']['base'] | sjson, n } + 'get_task_result/' + taskId+ '/';
                    wikiImportResult = await intervalGetCeleryTaskResult(getTaskResultUrl, 5000, WIKI_IMPORT_TIMEOUT, 'import wiki')
                    if (!wikiImportResult) {
                        return;
                    }
                    // The series of import processes has reached the end.
                    if (wikiImportResult.error_occurred) {
                        // show import error modal.
                        importErrors.push(...wikiImportResult.import_errors)
                        var importErrorMsg = createErrMsg(importErrors);
                        $('#importWiki').modal('hide');
                        $('#alertInfo').modal('hide');
                        $('#importResult').modal('show');
                        $('#showImportError').append('<p>' + importErrorMsg + '</p>')
                        $importResult.find('#showImportError').css('display', '');
                        $alertInfoForm.find('.btnAll').css('display', 'none');
                    } else {
                        $submitForm.attr('disabled', 'disabled').text('${_("Import Complete")}');
                        //rolaod
                        const reloadUrl = (location.href).replace(location.search, '')
                        window.location.assign(reloadUrl);
                    }
                    return;
                }).fail(function (response) {
                    if (response.status !== 0) {
                        alert('Error occurred when wiki import.');
                    }
                });
            });
        }

        async function intervalGetCeleryTaskResult(url, ms, timeout, operation) {
            console.log('interval get celery task result start')
            var count = 0;
            var result = '';
            var timeoutCtn = timeout * 1000 / ms
            console.log(timeoutCtn);
            while (count < timeoutCtn) {
                console.log('interval start')
                await new Promise(function(resolve){
                    setTimeout(async function(){
                        result = await getCeleryTaskResult(url, operation)
                        resolve();
                    }, ms);
                });
                if (result) {
                    break;
                }
                count++;
            }
            if (count === timeoutCtn){
                alert('timeout the operation');
                return;
            }
            return result;
        }

        async function getCeleryTaskResult(getCeleryTaskUrl, operation) {
            console.log('get celery task result start')
            return $.ajax({
                type: 'GET',
                cache: false,
                url: getCeleryTaskUrl,
                dataType: 'json',
            }).fail(function (response) {
                if (response.status !== 0) {
                    alert('error when ' + operation);
                    const reloadUrl = (location.href).replace(location.search, '')
                    return;
                }
            });     
        }

        async function abortCeleryTask(taskId) {
            console.log('abort celery task start')
            var abortTaskUrl = ${ urls['api']['base'] | sjson, n } + 'abort_celery_task/' + taskId+ '/';
            return $.ajax({
                type: 'GET',
                cache: false,
                url: abortTaskUrl,
                dataType: 'json',
            }).done(function (response) {
                const reloadUrl = (location.href).replace(location.search, '')
                window.location.assign(reloadUrl);
            }).fail(function (response) {
                if (response.status !== 0) {
                    console.log(response)
                    alert(response.message_long);
                    const reloadUrl = (location.href).replace(location.search, '')
                    window.location.assign(reloadUrl);
                    return;
                }
            });
        }

        async function getMdContentFromWB(mfr_url, data, $submitForm, totalCtn) {
            return $.ajax({
                type: 'GET',
                url: mfr_url,
                dataType: 'text',
                beforeSend: function (xhr, options) {
                    if (navigator.appVersion.indexOf('MSIE 9.') === -1) {
                        xhr.withCredentials = true;
                        xhr.fileName = data.name;
                        xhr.parentWikiName = data.parent_wiki_name;
                        xhr.path = data.path;
                        xhr.validation = data.status;
                        xhr.numbering = data.numbering;
                        if (options) {
                            options.withCredentials = true;
                            options.xhrFields = {withCredentials:true};
                        }
                    }
                    return xhr;
                }
            }).done(function (parsed, status, response) {
                readingCtn = readingCtn + 1;
                $submitForm.attr('disabled', 'disabled').text('${_("Reading Wiki Contents")}' + readingCtn + '/' + totalCtn);
                wiki_info.push({path: response.path, wiki_name: response.fileName, wiki_content: response.responseText, parent_wiki_name: response.parentWikiName, validation: response.validation, numbering: response.numbering});
            }).fail(function (response) {
                importErrors.push({'wb': response.fileName})
            })
        }
        function createErrMsg(errorList) {
            var errMsg = 'The following wiki pages could not be imported.';
            var errWB = '<br>< failed to get the text from markdown file >';
            var errImportProcess = '<br>< failed to import process >';
            var flgErrWB = false;
            var flgErrorImportProcess = false;
            for (var i = 0; i < errorList.length; i++) {
                if (Object.keys(errorList[i])[0] === 'wb') {
                    flgErrWB = true;
                    errWB += '<br>' + errorList[i].wb;
                } else if (Object.keys(errorList[i])[0] === 'import_error') {
                    flgErrorImportProcess = true;
                    errImportProcess += '<br>' + errorList[i].import_error;
                }
            }
            if (flgErrWB) {
                errMsg += errWB;
            }
            if (flgErrorImportProcess) {
                errMsg += errImportProcess;
            }
            return errMsg;
        }
        function fixToImportList(operation, validationResultCopy, perOperationList) {
            console.log('---fixtoimportlist start---');
            if (operation === null && perOperationList.length > 0) {
                for (var m=validationResultCopy.length-1; m>=0; m--) {
                    if (validationResultCopy[m].status === 'invalid') {
                        validationResultCopy.splice(m, 1);
                        continue;
                    }
                    for (var n=0; n<perOperationList.length; n++) {
                        if (validationResultCopy[m].name === perOperationList[n].wiki_name) {
                            if (perOperationList[n].operation === 'skip') {
                                console.log('---per action skip---')
                                validationResultCopy.splice(m, 1);
                                break;
                            } else if (perOperationList[n].operation === 'overwrite') {
                                console.log('---per action overwrite---')
                                break;
                                // no deal
                            } else if (perOperationList[n].operation === 'createNew') {
                                console.log('---per action createNew---')
                                if ((validationResultCopy[m].status).startsWith('valid_')){
                                    validationResultCopy[m].name = validationResultCopy[m].name + '(' + validationResultCopy[m].numbering + ')';
                                }
                                break;
                            }
                        }
                    }
                }
            } else if (operation === 'skipAll' || operation === '') {
                for (var i=validationResultCopy.length-1; i>=0; i--) {
                    if (validationResultCopy[i].status !== 'valid' && validationResultCopy[i].status !== 'valid_duplicated') {
                        validationResultCopy.splice(i, 1);
                    }
                }
            } else if (operation === 'overwriteAll') {
                for (var j=validationResultCopy.length-1; j>=0; j--) {
                    if (validationResultCopy[j].status === 'invalid') {
                        validationResultCopy.splice(j, 1);
                    }
                }
            } else if (operation === 'createNewAll') {
                for (var k=validationResultCopy.length-1; k>=0; k--) {
                    if (validationResultCopy[k].status === 'invalid') {
                        validationResultCopy.splice(k, 1);
                    } else if (validationResultCopy[k].status === 'valid_exists') {
                        validationResultCopy[k].name = validationResultCopy[k].name + '(' + validationResultCopy[k].numbering + ')';
                    }
                }
            } else {
                // as skipAll
                for (var m=validationResultCopy.length-1; m>=0; m--) {
                    if (validationResultCopy[m].status !== 'valid' && validationResultCopy[i].status !== 'valid_duplicated') {
                        validationResultCopy.splice(m, 1);
                    }
                }
            }
            return validationResultCopy;
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
            }).fail(function (response) {
                if (response.status !== 0) {
                    alert('error create sub folder: ' + folderName);
                    return;
                }
            });
        };
        function getOrCreateWikiImportFolder(imageFolder, dir_id) {
            var folderUrl = ${ urls['api']['base'] | sjson, n } + 'get_imported_wiki_workspace/' + dir_id + '/';
            return $.ajax({
                url: folderUrl,
                type: 'POST',
                dataType: 'json'
            }).then(function(response) {
                var link = window.contextVars.waterbutlerURL + 'v1/resources/' + window.contextVars.node.id + '/providers/osfstorage' + response.path + '?kind=folder';
                if (response.exist) {
                    return createSubFolder(link, Math.random().toString(32).substring(2)).then(function(response) {
                        return response.data.attributes.path;
                    });
                } else {
                    return createSubFolder(link, importFolder).then(function(response) {
                        return createSubFolder(response.data.links.new_folder, Math.random().toString(32).substring(2)).then(function(response) {
                            return response.data.attributes.path;
                        });
                    });
                }
            }).fail(function (response) {
                if (response.status !== 0) {
                    alert('error, possibly Wiki images failed to create or nothing.')
                    return;
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
                    for (var i = 0, folder; folder = response.data[i]; i++) {
                        var name = folder.attributes.name;
                        var id = folder.id;
                        if (name === imageFolder) {
                            return getOrCreateWikiImportFolder(importFolder, id);
                        }
                    }
                }
                if (response.data.length === 0) {
                    return createFolder(imageFolder).then(function(response) {
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

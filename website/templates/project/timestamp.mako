<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Timestamp</%def>

<div class="page-header  visible-xs">
    <h2 class="text-300">Timestamp</h2>
</div>

<div class="row">
    <div class="col-sm-5">
        <h2 class="break-word">Timestamp Control</h2>
    </div>
    <div class="col-sm-7">
        <div id="toggleBar" class="pull-right"></div>
    </div>
</div>

<hr/>

<div class="row project-page">

    <!-- Begin left column -->
    <div class="col-md-3 col-xs-12 affix-parent scrollspy">
        <div class="panel panel-default osf-affix" data-spy="affix" data-offset-top="0" data-offset-bottom="263">
            <!-- Begin sidebar -->
            <ul class="nav nav-stacked nav-pills">
                <li class="active">
                    <a href="#">Timestamp Error</a>
                </li>
            </ul>
        </div>
    </div>

    <div class="col-md-9 col-xs-12">
        <div id="timestamp-form" class="form">
            <div class="row">
                <div class="col-xl-8 col-lg-10 col-sm-12">
                    <form>
                        <div class="form-group row">
                            <div class="col-sm-6">
                                <div class="input-group">
                                    <div class="input-group-addon">Start Date</div>
                                    <input id="startDateFilter" type="date" class="form-control" />
                                </div>
                            </div>
                            <div class="col-sm-6">
                                <div class="input-group">
                                    <div class="input-group-addon">End Date</div>
                                    <input id="endDateFilter" type="date" class="form-control" />
                                </div>
                            </div>
                            <div class="col-sm-6">
                                <div class="input-group">
                                    <div class="input-group-addon">User</div>
                                    <select id="userFilterSelect" class="form-control">
                                        <option value=""></option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-sm-12">
                                <button type="reset" class="btn btn-primary">Reset</button>
                                <button type="button" class="btn btn-primary" id="applyFiltersButton">Apply</button>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="col-sm-12" style="margin-bottom: 10px;">
                    <div class="row">
                        <div class="col-sm-7">
                            <span>
                                <button type="button" class="btn btn-success" id="btn-verify">Verify</button>
                                <button type="button" class="btn btn-success" id="btn-addtimestamp">Request Trusted Timestamp</button>
                            </span>
                        </div>
                        <div class="col-sm-3">
                            <span>
                                <select id="fileFormat" class="form-control">
                                    <option value="csv">CSV</option>
                                    <option value="json-ld">JSON/LD</option>
                                    <option value="rdf-xml">RDF/XML</option>
                                </select>
                            </span>
                        </div>
                        <div class="col-sm-2">
                            <span>
                                <button type="button" class="btn btn-success" id="btn-download">Download</button>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <span id="configureNodeAnchor" class="anchor"></span>
            <div class="row">
                <div class="col-xs-12">
                    <table class="table table-bordered table-addon-terms">
                        <thead class="block-head">
                            <tr>
                                <th width="3%">
                                    <input type="checkBox" id="addTimestampAllCheck" style="width: 15px; height: 15px;"/>
                                </th>
                                <th width="40%">File Path</th>
                                <th width="15%">Timestamp Update User</th>
                                <th width="22%">Timestamp Update Date</th>
                                <th widht="20%">Timestamp Verification</th>
                            </tr>
                        </thead>
                        <font color="red">
                            <div id="timestamp_errors_spinner" class="spinner-loading-wrapper">
                                <div class="logo-spin logo-lg"></div>
                                <p class="m-t-sm fg-load-message"> Loading timestamp error list ...  </p>
                            </div>
                        </font>
                        <tbody class="list" id="timestamp_error_list">
                            % for provider_error_info in provider_list:
                            <tr>
                                <td colspan="5">
                                    <b>${ provider_error_info['provider'] }</b>
                                </td>
                            </tr>
                            % for error_info in provider_error_info['error_list']:
                            <tr class="addTimestamp">
                                <td>
                                    <input type="checkBox" class="check" id="addTimestampCheck" style="width: 15px; height: 15px;"/>
                                </td>
                                <td>${ error_info['file_path'] }
                                    <input type="hidden" name="provider" class="provider" value="${ provider_error_info['provider'] }" />
                                    <input type="hidden" name="file_id" class="file_id" value="${ error_info['file_id'] }" />
                                    <input type="hidden" name="file_path" class="file_path" value="${ error_info['file_path'] }" />
                                    <input type="hidden" name="version" class="version" value="${ error_info['version'] }" />
                                    <input type="hidden" name="file_name" class="file_name" value="${ error_info['file_name'] }" />
                                    <input type="hidden" name="creator_name" value="${ error_info['creator_name'] }" />
                                    <input type="hidden" name="creator_email" value="${ error_info['creator_email'] }" />
                                    <input type="hidden" name="creator_id" value="${ error_info['creator_id'] }" />
                                    <input type="hidden" name="creator_institution" value="${ error_info['creator_institution'] }" />
                                </td>
                                <td class="operator_user">${ error_info['operator_user'] } (${ error_info['operator_user_id'] })</td>
                                <td class="operator_date">${ error_info['operator_date'] }</td>
                                <td>${ error_info['verify_result_title'] }</td>
                            </tr>
                            % endfor
                            % endfor
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<style type="text/css">
.table>thead>tr>th {
    vertical-align: middle;
}
.form-group .input-group {
    margin-bottom: 10px;
}
date-input-polyfill {
  z-index: 3;
}
</style>

<%def name="javascript_bottom()">
${parent.javascript_bottom()}
% for script in tree_js:
<script type="text/javascript" src="${script | webpack_asset}"></script>
% endfor
<script src=${"/static/public/js/timestamp-page.js" | webpack_asset}></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/nodep-date-input-polyfill@5.2.0/nodep-date-input-polyfill.dist.min.js"></script>
</%def>

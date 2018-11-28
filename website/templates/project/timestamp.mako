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
        <form id="timestamp-form" class="form">
            <div class="row">
                <div class="col-xs-6">
                    <div class="form-inline">
                        <div class="form-group">
                            <div class="input-group">
                                <div class="input-group-addon">Start Date</div>
                                <input id="startDateFilter" type="datetime-local" class="form-control" />
                            </div>
                            <br />
                            <br />
                            <div class="input-group">
                                <div class="input-group-addon">End Date</div>
                                <input id="endDateFilter" type="datetime-local" class="form-control" />
                            </div>
                            <br />
                            <br />
                            <div class="input-group">
                                <div class="input-group-addon">User</div>
                                <select id="userFilterSelect" class="form-control">
                                    <option value=""></option>
                                </select>
                            </div>
                        </div>
                        <br />
                        <br />
                        <button type="button" class="btn btn-primary" id="applyFiltersButton">Apply</button>&nbsp;
                    </div>
                </div>
                <div class="col-xs-6">
                    <span>
                        <button type="button" class="btn btn-success" id="btn-verify">Verify</button>
                        <button type="button" class="btn btn-success" id="btn-addtimestamp">Request Trusted Timestamp</button>
                    </span>
                </div>
            </div>
            <br />
            <span id="configureNodeAnchor" class="anchor"></span>
            <div class="row">
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
                                <input type="checkBox" id="addTimestampCheck" style="width: 15px; height: 15px;"/>
                            </td>
                            <td>${ error_info['file_path'] }
                                <input type="hidden" name="provider" id="provider" value="${ provider_error_info['provider'] }" />
                                <input type="hidden" name="file_id" id="file_id" value="${ error_info['file_id'] }" />
                                <input type="hidden" name="file_path" id="file_path" value="${ error_info['file_path'] }" />
                                <input type="hidden" name="version" id="version" value="${ error_info['version'] }" />
                                <input type="hidden" name="file_name" id="file_name" value="${ error_info['file_name'] }" />
                            </td>
                            <td class="operator_user">${ error_info['operator_user'] }</td>
                            <td class="operator_date">${ error_info['operator_date'] }</td>
                            <td>${ error_info['verify_result_title'] }</td>
                        </tr>
                        % endfor
                        % endfor
                    </tbody>
                </table>
            </div>
        </form>
    </div>
</div>

<style type="text/css">
.table>thead>tr>th {
vertical-align: middle;
}
</style>

<%def name="javascript_bottom()">
${parent.javascript_bottom()} 
% for script in tree_js:
<script type="text/javascript" src="${script | webpack_asset}"></script>
% endfor
<script src=${"/static/public/js/timestamp-page.js" | webpack_asset}></script>
</%def>

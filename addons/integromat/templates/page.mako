<%inherit file="project/project_base.mako"/>
<%def name="title()">Integromat - ${node['title']}</%def>
<div class="row project-page">
% if has_auth:
    % if not is_registration:
    <!-- Begin left column -->
    <div class="col-md-3 col-xs-12 affix-parent scrollspy">

            <div class="panel panel-default osf-affix" data-spy="affix" data-offset-top="0" data-offset-bottom="263"><!-- Begin sidebar -->
                <ul class="nav nav-stacked nav-pills">

                        <li><a href="#" onClick="view_reg();return false;">Regster Conference</a></li>

                        <li><a href="#" onClick="view_update();return false;">Update Conference</a></li>

                        <li><a href="#" onClick="view_del();return false;">Delete Conference</a></li>

                        <li><a href="#" onClick="view_all();return false;">Schedule Conference</a></li>

        <!--            <li><a href="#" onClick="view_rec();return false;">Record Conference</a></li>  -->


                </ul>
            </div><!-- End sidebar -->
    </div>

    <!-- End left column -->
    <div class="col-md-9 col-xs-12">
    <div id="registerConf" style="display: none;">
      <div class="row tb-header-row">
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;REGISTER SCHEDULE
          <button href="#integromatRegisterConferenceModal" data-toggle="modal"  class="text-success pull-right" style="border: 1px solid #DDD;"><i class="fa fa-plus"></i><span>Register Conference</span></button>
      </div>
        <div class="row" id="pagination-row">
            <div class="col-sm-8">
                <ul class="pagination-wrap" style="display: none;">
                    <li class="pagination-prev">
                        <a class="page">&#060;</a>
                    </li>
                    <ul class="listjs-pagination"></ul>
                    <li class="pagination-next">
                        <a class="page">&#062;</a>
                    </li>
                </ul>
            </div>
            <div class="col-sm-2">
                <label class="pull-right" style="margin: 20px 0;">per page:</label>
            </div>
            <div class="col-sm-2">
                <select id="pageLength" class="form-control" style="margin: 15px 0;">
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="30">30</option>
                </select>
            </div>
        </div>
        <div class="row" id="teamsConference-table-row" style="width: 90%">
            <div class="col-xs-12">
                <table class="table table-bordered table-addon-terms">
                    <thead class="block-head">
                        <tr style="background-color: #f5f5f5;">
                            <th width="3%">
                                <input type="checkBox" id="addTimestampAllCheck" style="width: 15px; height: 15px;"/>
                            </th>
                            <th width="14%">
                                <span class="sorter">
                                    <i id="sort_up_provider" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_provider" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Provider">Start Date</span>
                            </th>
                            <th width="29%">
                                <span class="sorter">
                                    <i id="sort_up_file_path" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_file_path" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="File Path">Topic</span>
                            </th>
                            <th width="15%">
                                <span class="sorter">
                                    <i id="sort_up_verify_user_name_id" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_user_name_id" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp by">Meeting ID</span>
                            </th>
                            <th width="19%">
                                <span class="sorter">
                                    <i id="sort_up_verify_date" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_date" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Updated at">Host</span>
                            </th>
                            <th width="20%">
                                <span class="sorter">
                                    <i id="sort_up_verify_result_title" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_result_title" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp Verification">Invitation URL</span>
                            </th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>
    <div id="updateConf" style="display: none;">
      <div class="row tb-header-row">
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;UPDATE SCHEDULE
          <button class="text-info pull-right" style="border: 1px solid #DDD;"><i class="fa fa-edit"></i><span>Update Conference</span></button>
      </div>
        <div class="row" id="pagination-row">
            <div class="col-sm-8">
                <ul class="pagination-wrap" style="display: none;">
                    <li class="pagination-prev">
                        <a class="page">&#060;</a>
                    </li>
                    <ul class="listjs-pagination"></ul>
                    <li class="pagination-next">
                        <a class="page">&#062;</a>
                    </li>
                </ul>
            </div>
            <div class="col-sm-2">
                <label class="pull-right" style="margin: 20px 0;">per page:</label>
            </div>
            <div class="col-sm-2">
                <select id="pageLength" class="form-control" style="margin: 15px 0;">
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="30">30</option>
                </select>
            </div>
        </div>
        <div class="row" id="teamsConference-table-row" style="width: 90%">
            <div class="col-xs-12">
                <table class="table table-bordered table-addon-terms">
                    <thead class="block-head">
                        <tr style="background-color: #f5f5f5;">
                            <th width="3%">
                                <input type="checkBox" id="addTimestampAllCheck" style="width: 15px; height: 15px;"/>
                            </th>
                            <th width="14%">
                                <span class="sorter">
                                    <i id="sort_up_provider" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_provider" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Provider">Start Date</span>
                            </th>
                            <th width="29%">
                                <span class="sorter">
                                    <i id="sort_up_file_path" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_file_path" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="File Path">Topic</span>
                            </th>
                            <th width="15%">
                                <span class="sorter">
                                    <i id="sort_up_verify_user_name_id" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_user_name_id" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp by">Meeting ID</span>
                            </th>
                            <th width="19%">
                                <span class="sorter">
                                    <i id="sort_up_verify_date" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_date" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Updated at">Host</span>
                            </th>
                            <th width="20%">
                                <span class="sorter">
                                    <i id="sort_up_verify_result_title" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_result_title" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp Verification">Invitation URL</span>
                            </th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>
    <div id="deleteConf" style="display: none;">
      <div class="row tb-header-row">
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DELETE SCHEDULE
          <button class="text-danger pull-right" style="border: 1px solid #DDD;"><i class="fa fa-trash"></i><span>Delete Conference</span></button>
      </div>
        <div class="row" id="pagination-row">
            <div class="col-sm-8">
                <ul class="pagination-wrap" style="display: none;">
                    <li class="pagination-prev">
                        <a class="page">&#060;</a>
                    </li>
                    <ul class="listjs-pagination"></ul>
                    <li class="pagination-next">
                        <a class="page">&#062;</a>
                    </li>
                </ul>
            </div>
            <div class="col-sm-2">
                <label class="pull-right" style="margin: 20px 0;">per page:</label>
            </div>
            <div class="col-sm-2">
                <select id="pageLength" class="form-control" style="margin: 15px 0;">
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="30">30</option>
                </select>
            </div>
        </div>
        <div class="row" id="teamsConference-table-row" style="width: 90%">
            <div class="col-xs-12">
                <table class="table table-bordered table-addon-terms">
                    <thead class="block-head">
                        <tr style="background-color: #f5f5f5;">
                            <th width="3%">
                                <input type="checkBox" id="addTimestampAllCheck" style="width: 15px; height: 15px;"/>
                            </th>
                            <th width="14%">
                                <span class="sorter">
                                    <i id="sort_up_provider" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_provider" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Provider">Start Date</span>
                            </th>
                            <th width="29%">
                                <span class="sorter">
                                    <i id="sort_up_file_path" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_file_path" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="File Path">Topic</span>
                            </th>
                            <th width="15%">
                                <span class="sorter">
                                    <i id="sort_up_verify_user_name_id" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_user_name_id" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp by">Meeting ID</span>
                            </th>
                            <th width="19%">
                                <span class="sorter">
                                    <i id="sort_up_verify_date" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_date" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Updated at">Host</span>
                            </th>
                            <th width="20%">
                                <span class="sorter">
                                    <i id="sort_up_verify_result_title" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_result_title" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp Verification">Invitation URL</span>
                            </th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>
    <div id="allConference" style="display: none;">
      <div class="row tb-header-row">
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;CONFERENCE SCHEDULE
          <button class="text-danger pull-right" style="border: 1px solid #DDD;"><i class="fa fa-trash"></i><span>Delete Conference</span></button>
          <button class="text-info pull-right" style="border: 1px solid #DDD;"><i class="fa fa-edit"></i><span>Update Conference</span></button>
          <button href="#integromatRegisterConferenceModal" data-toggle="modal"  class="text-success pull-right" style="border: 1px solid #DDD;"><i class="fa fa-plus"></i><span>Register Conference</span></button>
      </div>
        <div class="row" id="pagination-row">
            <div class="col-sm-8">
                <ul class="pagination-wrap" style="display: none;">
                    <li class="pagination-prev">
                        <a class="page">&#060;</a>
                    </li>
                    <ul class="listjs-pagination"></ul>
                    <li class="pagination-next">
                        <a class="page">&#062;</a>
                    </li>
                </ul>
            </div>
            <div class="col-sm-2">
                <label class="pull-right" style="margin: 20px 0;">per page:</label>
            </div>
            <div class="col-sm-2">
                <select id="pageLength" class="form-control" style="margin: 15px 0;">
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="30">30</option>
                </select>
            </div>
        </div>
        <div class="row" id="teamsConference-table-row" style="width: 90%">
            <div class="col-xs-12">
                <table class="table table-bordered table-addon-terms">
                    <thead class="block-head">
                        <tr style="background-color: #f5f5f5;">
                            <th width="3%">
                                <input type="checkBox" id="addTimestampAllCheck" style="width: 15px; height: 15px;"/>
                            </th>
                            <th width="14%">
                                <span class="sorter">
                                    <i id="sort_up_provider" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_provider" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Provider">Start Date</span>
                            </th>
                            <th width="29%">
                                <span class="sorter">
                                    <i id="sort_up_file_path" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_file_path" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="File Path">End Date</span>
                            </th>
                            <th width="15%">
                                <span class="sorter">
                                    <i id="sort_up_verify_user_name_id" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_user_name_id" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp by">Attendees</span>
                            </th>
                            <th width="19%">
                                <span class="sorter">
                                    <i id="sort_up_verify_date" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_date" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Updated at">Host</span>
                            </th>
                            <th width="20%">
                                <span class="sorter">
                                    <i id="sort_up_verify_result_title" class="fa fa-chevron-up tb-sort-inactive asc-btn m-r-xs"></i>
                                    <i id="sort_down_verify_result_title" class="fa fa-chevron-down tb-sort-inactive desc-btn"></i>
                                </span>
                                <span class="header_text m-r-sm" title="Timestamp Verification">Invitation URL</span>
                            </th>
                        </tr>
                    </thead>
                </table>
            </div>
        </div>
    </div>
    </div>
</div>

<div id="integromatRegisterConferenceModal" class="modal fade" style="display: none;">
    <div class="modal-dialog text-lef">
        <div class="modal-content">

            <div class="modal-header">
                <h3>Register Teams Conference</h3>
            </div>

            <form>
                <div class="modal-body">

                            <div class="form-group">
                                <input type="hidden" name="teams_Guid" id="teams_guid" value="${node['id']}">
                                <input type="hidden" name="teams_Action" id="teams_action" value="teams_action">
                                <label >Subject</label>
                                <input class="form-control" data-bind="value: teamsSubject" id="teams_subject" name="teams_Subject" placeholder="input teams meeting subject"/>
                            </div>
                            <div class="form-group">
                                <label >Attendees</label>
                                <input class="form-control" data-bind="value: teamsAttendees" id="teams_attendees" name="teams_Attendees" placeholder="input teams meeting attendees"/>
                            </div>
                            <div class="form-group">
                                <label >Start Date and Time</label>
                                <input class="form-control" data-bind="value: teamsStartDate" id="teams_start_date" name="teams_Start_Date" placeholder="YYYY/MM/DD"/>
                                <input type="time" step="1800" class="form-control" data-bind="value: teamsStartTime" id="teams_start_time" name="teams_Start_Time" min="00:00" max="23:59">
                                <label >End Date and Time</label>
                                <input class="form-control" data-bind="value: teamsEndDate" id="teams_end_date" name="teams_End_Date" placeholder="YYYY/MM/DD"/>
                                <input type="time" step="1800" class="form-control" data-bind="value: teamsEndTime" id="teams_end_time" name="teams_End_Time" min="00:00" max="23:59">
                            </div>
                            <div class="form-group">
                                <label >Location</label>
                                <input class="form-control" data-bind="value: teamsLocation" id="teams_location" name="teams_Location" placeholder="input teams meeting location"/>
                            </div>
                            <div class="form-group">
                                <label >Content</label>
                                <textarea class="form-control" data-bind="value: teamsContent" id="teams_content" name="teams_Content" /></textarea>
                            </div>

                    <!-- Flashed Messages -->
                    <div class="help-block">
                        <p data-bind="html: message, attr: {class: messageClass}"></p>
                    </div>

                </div><!-- end modal-body -->

                <div class="modal-footer">

                    <a href="#" class="btn btn-default" data-bind="click: clearModal" data-dismiss="modal">Cancel</a>

                    <!-- Save Button -->
                    <button id="startScenario" class="btn btn-success">Register</button>

                </div><!-- end modal-footer -->

            </form>

        </div><!-- end modal-content -->
    </div>
    % endif
% else:
        Please
        <a href="#integromatCredentialsModal" data-toggle="modal">
        Connect Account
        </a>
% endif
</div>


<script language="JavaScript" type="text/javascript">
var reg = document.getElementById("registerConf");
var update = document.getElementById("updateConf");
var del = document.getElementById("deleteConf");
var all = document.getElementById("allConference");

function view_reg() {
  reg.style.display = "";
  update.style.display = "none";
  del.style.display = "none";
  all.style.display = "none";
}
function view_update() {
  update.style.display = "";
  reg.style.display = "none";
  del.style.display = "none";
  all.style.display = "none";
}
function view_del() {
  del.style.display = "";
  update.style.display = "none";
  reg.style.display = "none";
  all.style.display = "none";
}
function view_all() {
  all.style.display = "";
  update.style.display = "none";
  del.style.display = "none";
  reg.style.display = "none";
}
</script>

<script src=${"/static/public/js/integromat.js" | webpack_asset}></script>
#coding=utf-8
<%page args="t"/>
<% langs=['en'] %>

<input type="hidden" name="existing_contributors" id="existing_contributors" value="${content['contributors']}" />
% for lang in langs:
<div id="manageContributors" style="border-top: 1px solid #ddd;">
    <h3> ${t[lang]['Contributors']}
        <a href="#addContributors" data-toggle="modal" class="btn btn-success btn-sm m-l-md">
            <i class="fa fa-plus"></i> Add
        </a>
    </h3>

    % if 'admin' in user['permissions'] and not node['is_registration']:
    <p class="m-b-xs">${t[lang]['Drag and drop contributors to change listing order.']}</p>
    % endif

    <div data-bind="filters: {
        items: ['.contrib', '.admin'],
        toggleClass: 'btn-default btn-primary',
        manualRemove: true,
        groups: {
            permissionFilter: {
                filter: '.permission-filter',
                type: 'text',
                buttons: {
                    admins: 'Administrator',
                    write: 'Read + Write',
                    read: 'Read'
                }
            },
            visibleFilter: {
                filter: '.visible-filter',
                type: 'checkbox',
                buttons: {
                    visible: true,
                    notVisible: false
                }
            }
        },
        inputs: {
            nameSearch: '.name-search'
        }
    }">
        <table id="manageContributorsTable"
               class="table responsive-table responsive-table-xxs"
               data-bind="template: {
                   name: 'contribTable',
                   afterRender: afterRender,
                   options: {
                       containment: '#manageContributors'
                   },
                   data: 'contrib'
               }">
        </table>
    </div>
    <div data-bind="visible: $root.empty" class="no-items text-danger m-b-md">
        ${t[lang]['No contributors found']}
    </div>
    <span id="adminContributorsAnchor" class="project-page anchor"></span>
    <div id="adminContributors" data-bind="if: adminContributors().length">
        <h4>
            ${t[lang]['Admins on Parent Projects']}
            <i class="fa fa-question-circle admin-info"
               data-content="These users are not contributors on
          this component but can view and register it because they
            are administrators on a parent project."
               data-toggle="popover"
               data-title="Admins on Parent Projects"
               data-container="body"
               data-placement="right"
               data-html="true"
            ></i>
        </h4>
        <table id="adminContributorsTable"
               class="table responsive-table responsive-table-xxs"
               data-bind="template: {
            name: 'contribTable',
            afterRender: afterRender,
            options: {
                containment: '#manageContributors'
            },
            data: 'admin'
        }">
        </table>
        <div id="noAdminContribs" data-bind="visible: $root.adminEmpty" class="text-danger no-items m-b-md">
            ${t[lang]['No administrators from parent project found.']}
        </div>
    </div>
    ${buttonGroup()}
</div>

<div id="${lang}_contributors-extensions" data-bind="visible: editingContributor">
    <div class="panel panel-default base-contributors-extensions">
        <span class="anchor"></span>
        <div class="panel-heading clearfix">
            <h3 class="panel-title" data-bind="text: contribInstance().userName">Sample Contributor</h3>
        </div>
        <div class="panel-body">
            <div class="form-group">
                <label for="title">${t[lang]['Permission']}</label>
                <input type="checkbox" class="biblio visible-filter" data-bind="checked: contribInstance().permission"/>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Visible']}</label>
                <input type="checkbox" data-bind="checked: contribInstance().visible" class="biblio visible-filter"/>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Type']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: contribInstance().contributorType" style="height:35px" >
                            <option value="">Choose...</option>
                            % for opt in dropdown_list['contributor_type']:
                            <option value="${opt[u'name']}">${opt[u'name']}</option>
                            % endfor
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Remarks']}</label>
                <textarea class="form-control" data-bind="text: contribInstance().contributorRemarks" type="text" maxlength="200" >テスト
                </textarea>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Assign Situation']}</label>
                <input class="form-control" type="text" data-bind="value: contribInstance().assignSituation" maxlength="200"/>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Representation Setting']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: contribInstance().representationSetting" style="height:35px" >
                            <option value="">Choose...</option>
                            % for opt in dropdown_list['contributor_repr']:
                            <option value="${opt[u'name']}">${opt[u'name']}</option>
                            % endfor
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Name']}</label>
                <input class="form-control" data-bind="value: contribInstance().name" type="text" maxlength="200"/>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Contributor Alternative']}</label>
            </div>
            <div class="form-group" >
                <div data-bind="foreach: contribInstance().alternatives">
                    <div class="form-group">
                        <i title="Click to remove" data-bind="click: $root.contribInstance().removeAlternative" class="btn text-danger pull-right  fa fa-times fa"></i>
                        <div class="input-group">
                            <span class="input-group-addon"><i title="Drag to reorder" class="fa fa-bars"></i></span>
                            <input type="url" data-bind="value: value" class="form-control"/>
                        </div>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <a class="btn btn-default" data-bind="click: contribInstance().addAlternative">${t[lang]['Add']}</a>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Organization Type']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: contribInstance().organizationType" style="height:35px">
                            <option value="">Choose...</option>
                            % for opt in dropdown_list['org_type']:
                            <option value="${opt[u'name']}">${opt[u'name']}</option>
                            % endfor
                        </select>
                    </div>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading clearfix">
                    <h3 class="panel-title" style="font-size:14px;font-weight: bold">${t[lang]['Idp']}</h3>
                </div>
                <div class="panel-body">
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp ID']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" data-bind="value: contribInstance().idpId" style="height:35px">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['ipd_identifier']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Affiliation Name']}</label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp Organization Habitation']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp Organization Phone Number']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp Organization Mail Address']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp Organization Icon']}</label>
                        <image width="50" height="30"
                                          src="http://www.themaulerinstitute.com/images/universities/boston-university-logo.jpg"></image>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Idp Organization Banner']}</label>
                        <image width="50" height="30"
                                          src="http://www.themaulerinstitute.com/images/universities/boston-university-logo.jpg"></image>
                    </div>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading clearfix">
                    <h3 class="panel-title" style="font-size:14px;font-weight: bold">${t[lang]['Organization']}</h3>
                </div>
                <div class="panel-body">
                    <div class="form-group">
                        <label for="title">${t[lang]['Research Organization ID']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" data-bind="value: contribInstance().researchOrganizationId" style="height:35px">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['research_org']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Recognition ID']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" data-bind="value: contribInstance().organizationRecognitionId" style="height:35px" >
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['org_recognition']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Abbreviation']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Stratum Relations']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Department Name']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Department English Name']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Country']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Zip Code']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Habitation']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Organization Web Url']}</label>
                        <label type="text" ></label>
                    </div>
                </div>
            </div>
            <div class="panel panel-default">
                <div class="panel-heading clearfix">
                    <h3 class="panel-title" style="font-size:14px;font-weight: bold">${t[lang]['Storage Department']}</h3>
                </div>
                <div class="panel-body">
                    <div class="form-group">
                        <label for="title">${t[lang]['Storage Department Organization Recognition ID']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" data-bind="value: contribInstance().storageDepOrganizationId" style="height:35px">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['storage_org']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Storage Department Name']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Storage Department En Name']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Storage Department Phone Number']}</label>
                        <label type="text" ></label>
                    </div>
                    <div class="form-group">
                        <label for="title">${t[lang]['Storage Department Mail Address']}</label>
                        <label type="text" ></label>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Version']}</label>
                <input type="checkbox" data-bind="checked: contribInstance().version" class="biblio visible-filter"/>
            </div>
            <div class="form-group">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-danger" data-bind="click: cancelContributor">${t[lang]['Close']}</button>
                        <button class="btn btn-default" data-bind="click: cancelContributor">${t[lang]['Cancel']}</button>
                        <button class="btn btn-success" data-bind="click: saveContributor">${t[lang]['Save Changes']}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
% endfor

<script id="contribTable" type="text/html">
    <thead>
        <tr>
            <th class="responsive-table-hide"
                data-bind="css: {sortable: ($data === 'contrib' && $root.isSortable())}">Name
            </th>
            <th></th>
            <th>
                Permissions
                <i class="fa fa-question-circle permission-info"
                    data-toggle="popover"
                    data-title="Permission Information"
                    data-container="body"
                    data-placement="right"
                    data-html="true"
                ></i>
            </th>
            <th class="biblio-contrib">
                Bibliographic Contributor
                <i class="fa fa-question-circle visibility-info"
                    data-toggle="popover"
                    data-title="Bibliographic Contributor Information"
                    data-container="body"
                    data-placement="right"
                    data-html="true"
                ></i>
            </th>
            <th class="remove"></th>
        </tr>
    </thead>
    <!-- ko if: $data == 'contrib' -->
    <tbody id="contributors" data-bind="sortable: {
            template: 'contribRow',
            data: $root.contributors,
            as: 'contributor',
            isEnabled: $root.isSortable
    }"></tbody>
    <!-- /ko -->
    <!--ko if: $data == 'admin' -->
        <tbody data-bind="template: {
            name: 'contribRow',
            foreach: $root.adminContributors,
            as: 'contributor',
        }">
    </tbody>
    <!-- /ko -->
</script>

<script id="contribRow" type="text/html">
    <tr data-bind="visible: !contributor.filtered(), click: unremove, css: {'contributor-delete-staged': $parent.deleteStaged}, attr: {class: $parent}">
        <td data-bind="attr: {class: contributor.expanded() ? 'expanded' : null,
                                role: $root.collapsed() ? 'button' : null},
                       click: $root.collapsed() ? toggleExpand : null">
            <!-- ko if: ($parent === 'contrib' && $root.isSortable()) -->
                <span class="fa fa-bars sortable-bars"></span>
                <img class="m-l-xs" data-bind="attr: {src: contributor.profile_image_url}" />
            <!-- /ko -->
            <!-- ko ifnot: ($parent === 'contrib' && $root.isSortable()) -->
                <img data-bind="attr: {src: contributor.profile_image_url}" />
            <!-- /ko -->
            <span data-bind="attr: {class: contributor.expanded() ? 'fa toggle-icon fa-angle-up' : 'fa toggle-icon fa-angle-down'}"></span>
            <div class="card-header">
                <span data-bind="ifnot: profileUrl">
                    <span class="name-search" data-bind="text: contributor.shortname"></span>
                </span>
                <span data-bind="if: profileUrl">
                    <a class="name-search" data-bind="text: contributor.shortname, attr:{href: profileUrl}"></a>
                </span>
                <span data-bind="text: permissionText()" class="permission-filter permission-search"></span>
            </div>
        </td>
        <td class="table-only">
            <span data-bind="ifnot: profileUrl">
                <span class="name-search" data-bind="text: contributor.shortname"></span>
            </span>
            <span data-bind="if: profileUrl">
                <a class="name-search" data-bind="text: contributor.shortname, attr:{href: profileUrl}"></a>
            </span>
        </td>
        <td class="permissions">
            <div class="header"></div>
            <div class="td-content">
                <!-- ko if: contributor.canEdit() -->
                    <span data-bind="visible: !deleteStaged()">
                        <select class="form-control input-sm" data-bind="
                            options: $parents[1].permissionList,
                            value: permission,
                            optionsText: optionsText.bind(permission),
                             style: { 'font-weight': permissionChange() ? 'normal' : 'bold' }"
                        >
                        </select>
                    </span>
                    <span data-bind="visible: deleteStaged">
                        <span data-bind="text: permissionText()"></span>
                    </span>
                    </span>
                <!-- /ko -->
                <!-- ko ifnot: contributor.canEdit() -->
                    <span data-bind="text: permissionText()"></span>
                <!-- /ko -->
            </div>
        </td>
        <td>
            <div class="header"></div>
            <div class="td-content">
                <input
                    type="checkbox" class="biblio visible-filter"
                    data-bind="checked: visible, enable: $data.canEdit() && !contributor.isParentAdmin && !deleteStaged()"
                />
            </div>
        </td>
        <td width="165">
            <div class="td-content">
                <!-- ko if: (contributor.canEdit() || canRemove) -->
                        <button href="#editContributor" class="btn btn-success btn-sm m-l-md" style="display: inline-block;" data-bind="value: id" onclick="editContributor(this.value)">Edit</button>
                        <button href="#removeContributor" class="btn btn-danger btn-sm m-l-md" style="display: inline-block;"
                           data-bind="click: remove"
                           data-toggle="modal">Remove</button>
                <!-- /ko -->
                <!-- ko if: (canAddAdminContrib) -->
                        <button class="btn btn-success btn-sm m-l-md"
                           data-bind="click: addParentAdmin"
                        ><i class="fa fa-plus"></i> Add</button>
                <!-- /ko -->
            </div>
        </td>
    </tr>
</script>

<%def name="buttonGroup()">
    % if 'admin' in user['permissions']:
    <div class="m-b-sm">
        <a class="btn btn-danger contrib-button" data-bind="click: cancel, visible: changed">Discard Changes</a>
        <a class="btn btn-success contrib-button" data-bind="click: submit, visible: canSubmit">Save Changes</a>
    </div>
    % endif
    <div data-bind="foreach: messages">
        <div data-bind="css: cssClass, text: text"></div>
    </div>
</%def>

<script type="text/javascript">
  window.contextVars = window.contextVars || {};
  window.contextVars.currentUser = window.contextVars.currentUser || {};
  window.contextVars.currentUser.permissions = ${ user['permissions'] | sjson, n } ;
  window.contextVars.isRegistration = ${ node['is_registration'] | sjson, n };
  window.contextVars.contributors = ${ contributors | sjson, n };
  window.contextVars.adminContributors = ${ adminContributors | sjson, n };
  window.contextVars.analyticsMeta = $.extend(true, {}, window.contextVars.analyticsMeta, {
      pageMeta: {
          title: 'Contributors',
          public: false,
      },
  });
</script>

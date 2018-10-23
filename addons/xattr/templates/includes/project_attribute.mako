#coding=utf-8
<%page args="t"/>
<% langs=['ja', 'en'] %>

% for lang in langs:
<div class="panel panel-default base-extensions" id="${lang}_projectAttribute">
    <span id="configureNodeAnchor" class="anchor"></span>
    <div class="panel-heading clearfix">
        <h3 id="configureNode" class="panel-title">${t[lang]['Project Extended Information Edit']}</h3>
    </div>
    <div class="panel-body">
        <div class="form-group">
            <label for="title">${t[lang]['Title']}</label>
            <input class="form-control" name="title" type="text" maxlength="200" value="${content[lang]['title']}" required="required"/>
        </div>
        <div class="form-group">
            <label>${t[lang]['Affiliation']}</label>
            <div class="row">
                <div class="col-md-6">
                    <select class="form-control" name="organizationUnit" required="required">
                        <option value="">Choose...</option>
                        % for opt in dropdown_list['proj_affiliation']:
                        <option value="${opt[u'name']}" ${'selected=selected' if opt['name'] == content[lang]['organizationUnit'] else ''}>${opt[u'name']}</option>
                        % endfor
                    </select>
                </div>
            </div>
        </div>
        <div class="form-group">
            <label>${t[lang]['Project Identification']}</label>
            <div class="row">
                <div class="col-md-6">
                    <select class="form-control project_identification" name="projectIdentification" required="required">
                        <option value="">Choose...</option>
                        % for opt in dropdown_list['proj_identifier']:
                        <option value="${opt[u'name']}" ${'selected=selected' if opt['name'] == content[lang]['projectIdentification'] else ''}>${opt[u'name']}</option>
                        % endfor
                    </select>
                </div>
            </div>
        </div>
        <div class="form-group">
            <label>${t[lang]['Research Field']}</label>
            <div class="row">
                <div class="col-md-6">
                    <select class="form-control research_field" name="researchField" required="required">
                        <option value="">Choose...</option>
                        % for opt in dropdown_list['research_field']:
                        <option value="${opt[u'name']}" ${'selected=selected' if opt['name'] == content[lang]['researchField'] else ''}>${opt[u'name']}</option>
                        % endfor
                    </select>
                </div>
            </div>
        </div>

        <div id="${lang}-range-list">
            <div class="panel panel-default scripted">
                <div class="well well-sm sort-handle">
                    <span data-bind="text: $parent.project_range">Sample Name</span>
                    <a class="text-danger pull-right remove-range">${t[lang]['Remove']}</a>
                </div>
                <div id="projectExtended" class="panel-body">
                    <div class="form-group">
                        <label>${t[lang]['Range Type']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" name="rangeType">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['range_type']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>${t[lang]['Range']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" name="range">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['range']:
                                    <option value="${opt[u'name']}">${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            % for i in range(len(content[lang]['rangeType'])):
            <div class="panel panel-default">
                <div class="well well-sm sort-handle">
                    <span data-bind="text: $parent.project_range">Sample Name</span>
                    <a class="text-danger pull-right remove-range">${t[lang]['Remove']}</a>
                </div>
                <div id="projectExtended" class="panel-body">
                    <div class="form-group">
                        <label>${t[lang]['Range Type']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" name="rangeType">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['range_type']:
                                    <option value="${opt[u'name']}" ${'selected=selected' if opt['name'] == content[lang]['rangeType'][i] else ''}>${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>${t[lang]['Range']}</label>
                        <div class="row">
                            <div class="col-md-6">
                                <select class="form-control" name="range">
                                    <option value="">Choose...</option>
                                    % for opt in dropdown_list['range']:
                                    <option value="${opt[u'name']}" ${'selected=selected' if opt['name'] == content[lang]['range'][i] else ''}>${opt[u'name']}</option>
                                    % endfor
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            % endfor
        </div>
        <div style="margin-bottom: 5px;">
            <a class="btn btn-default" id="${lang}-add-range">${t[lang]['Add']}</a>
        </div>
        <div class="form-group">
            <label>${t[lang]['Start Date']}</label>
            <div class="row">
                <div class="col-md-6">
                    <input type="date" class="StartDate form-control" name="startDate" value="${content[lang]['startDate']}" required="required"/>
                </div>
            </div>
        </div>
        <div class="form-group">
            <label>${t[lang]['End Date']}</label>
            <div class="row">
                <div class="col-md-6">
                    <input type="date" class="EndDate form-control" name="endDate" value="${content[lang]['endDate']}"/></div>
            </div>
        </div>
        <div class="form-group">
            <label for="title">${t[lang]['Description']}</label>
            <div class="row">
                <div class="col-md-12">
                    <textarea style="width: 100%;" name="description" class="col-md-12 form-control">${content[lang]['description']}</textarea>
                </div>
            </div>
        </div>
        <div class="form-group" style="margin-top: 15px;">
            <label>${t[lang]['Project Status']}</label>
            <div class="row">
                <div class="col-md-6">
                    <select class="form-control status" name="status">
                        <option value="1" ${'selected=selected' if content[lang]['status'] == '1' else ''}>${t[lang]['Start']}</option>
                        <option value="12" ${'selected=selected' if content[lang]['status'] == '12' else ''}>${t[lang]['Complete']}</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
</div>
% endfor

<script src="/static/vendor/knockout/knockout-3.0.0.min.js"></script>
<script src=${"https://www.gstatic.com/firebasejs/4.8.0/firebase.js" | webpack_asset}></script>

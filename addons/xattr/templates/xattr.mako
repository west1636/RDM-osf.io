<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Attributes</%def>

<%include file="project/modal_add_contributor.mako"/>
<%include file="project/modal_remove_contributor.mako"/>

<% lang='en' %>

<div class="page-header visible-sm">
    <h2 class="text-300">${t[lang]['Attributes']}</h2>
</div>

<div class="row project-page">
    <!-- Begin left column -->
    <div class="col-md-3 col-xs-12 affix-parent scrollspy">

        <div class="panel panel-default osf-affix" data-spy="affix" data-offset-top="0" data-offset-bottom="263">
            <!-- Begin sidebar -->
            <ul class="nav nav-stacked nav-pills">
                <li><a href="#configureNodeAnchor">${t[lang]['Base']}</a></li>
                <li><a href="#manageFunding" style="padding-top: 20px margin-top: -20px">${t[lang]['Fundings']}</a></li>
                <li><a href="#manageContributors">${t[lang]['Contributors']}</a></li>
            </ul>
            <!-- End sidebar -->
        </div>

    </div>
    <!-- End left column -->

    <!-- Begin right column -->
    <div class="col-sm-9 col-md-9" id="projectExtensionsPnl">
        <%include file="xattr/templates/includes/project_attribute.mako" args="t=t"/>
        <%include file="xattr/templates/includes/funding_attribute.mako" args="t=t"/>
        <%include file="xattr/templates/includes/contributor_attribute.mako" args="t=t"/>

        % if 'admin' in user['permissions']:
        <div style="display: none"><%include file="/project/private_links.mako"/></div>

        <div style="display: flex;">
            <div class="form-group" style="border-top: 2px solid #ddd;">
                <div class="row" style="padding-top: 20px;">
                    <div class="col-md-6">
                        <button class="btn btn-success" id="save-data">${t[lang]['Save']}</button>
                    </div>
                </div>
            </div>
            <div id="reset_div" style="margin-left: 10px;">
                <div class="form-group" style="border-top: 2px solid #ddd;">
                    <div class="row" style="padding-top: 20px;">
                        <div class="col-md-6">
                            <button class="btn btn-default" id="reset-data">${t[lang]['Cancel']}</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
		 % endif

        <div id="show_message">
            <div class="help-block">
                 <span data-bind="css: messageClass, text: message"></span>
            </div>
        </div>
    </div>
    <!-- End right column -->
</div>


<link rel="stylesheet" href="/static/css/pages/contributor-page.css">
<link rel="stylesheet" href="/static/css/responsive-tables.css">
<link rel="stylesheet" href="/static/css/pages/project-page.css">

<%def name="javascript_bottom()">
    ${parent.javascript_bottom()}
    <script type="text/javascript" src=${"/static/public/js/xattr/node-cfg.js" | webpack_asset}></script>
</%def>

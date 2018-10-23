<%inherit file="base.mako"/>
<%def name="title()">Attribute Profile Settings</%def>
<%def name="content()">
<h2 class="page-header">Settings</h2>

    <div id="userAttribute">
        <div class="row">
            <div class="col-md-3 affix-parent">
                <%include file="include/profile/settings_navpanel.mako" args="current_page='user_attribute'"/>
            </div>
            <div class="col-md-9 col-xs-12">
                <% langs=['ja', 'en'] %>

                % for lang in langs:
                    <div class="panel panel-default" id="${lang}_userAttribute">
                        <span id="configureNodeAnchor" class="anchor"></span>

                        <div class="panel-heading clearfix">
                            <h3 id="configureNode" class="panel-title">
                                ${t[lang]['User Extended Information Edit']}
                            </h3>
                        </div>

                        <div class="projectExtended panel-body">
                            <div class="form-group">
                                <label for="title">${t[lang]['Full Name (e.g. Yamada Taro)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="fullName" 
                                       value="${cont[lang]['fullName']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Full Name(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="fullNameKana"
                                       value="${cont[lang]['fullNameKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Given Name (e.g. Taro)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="givenName"
                                       value="${cont[lang]['givenName']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Given Name(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="givenNameKana"
                                       value="${cont[lang]['givenNameKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Middle Name']}</label>
                                <input class="form-control" type="text" maxlength="200" name="middleName"
                                       value="${cont[lang]['middleName']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Middle Name(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="middleNameKana"
                                       value="${cont[lang]['middleNameKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Family Name (e.g. Yamada)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="familyName"
                                       value="${cont[lang]['familyName']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Family Name(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="familyNameKana"
                                       value="${cont[lang]['familyNameKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Suffix']}</label>
                                <input class="form-control" type="text" maxlength="200" name="suffix"
                                       value="${cont[lang]['suffix']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Suffix(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name="suffixKana"
                                       value="${cont[lang]['suffixKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Alias']}</label>
                                <input class="form-control" type="text" maxlength="200" name="alias"
                                       value="${cont[lang]['alias']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Alias(kana)']}</label>
                                <input class="form-control" type="text" maxlength="200" name=aliasKana
                                       value="${cont[lang]['aliasKana']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['E-Rad ID']}</label>
                                <input class="form-control" type="text" maxlength="200" name="eRadId"
                                       value="${cont[lang]['eRadId']}" required="required">
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['ResearchMap ID']}</label>
                                <input class="form-control" type="text" maxlength="200" name="researchMapId"
                                       value="${cont[lang]['researchMapId']}" required="required">
                            </div>
                            ## TODO: commonmaster 
                            <div class="form-group">
                                <label for="title">${t[lang]['Organization Type']}</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <select class="form-control" style="height:30px" name="organizationType"
                                                value="${cont[lang]['organizationType']}" required="required">
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="panel panel-default">
                                <div class="panel-heading clearfix">
                                    <h3 class="panel-title" style="font-size:14px;font-weight: bold">
                                        ${t[lang]['Idp']}</h3>
                                </div>
                                ## TODO: commonmaster 
                                <div class="panel-body">
                                    <div class="form-group">
                                        <label for="title">${t[lang]['Idp']}</label>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <select class="col-md-12 form-control" style="height:30px" name="idp"
                                                        value="${cont[lang]['idp']}" required="required">
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Idp Organization Name']}
                                        </label>
                                        <label type="text" name="idpName">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title" name="idpHabitation">
                                            ${t[lang]['Idp Organization Habitation']}</label>
                                        <label type="text">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title" name="idpPhoneNumber">
                                            ${t[lang]['Idp Organization Phone Number']}
                                        </label>
                                        <label type="text">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title" name="idpAddress">
                                            ${t[lang]['Idp Organization Address']}
                                        </label>
                                        <label type="text">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Idp Organization Icon']}
                                        </label>
                                    </div>
                                    <div class="form-group" name="idpIcon">
                                        <image width="50" height="30"
                                               src="http://www.themaulerinstitute.com/images/universities/boston-university-logo.jpg">
                                        </image>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">${t[lang]['Idp Organization Banner']}</label>
                                    </div>
                                    <div class="form-group" name="idpBanner">
                                        <image width="50" height="30"
                                               src="http://www.themaulerinstitute.com/images/universities/boston-university-logo.jpg">
                                        </image>
                                    </div>
                                </div>
                            </div>
    
                            <div class="panel panel-default">
                                 <div class="panel-heading clearfix">
                                    <h3 class="panel-title" style="font-size:14px;font-weight: bold">
                                        ${t[lang]['Organization']}</h3>
                                </div>
                                <div class="panel-body">
                                    ## TODO: commonmaster 
                                    <div class="form-group">
                                        <label for="title">${t[lang]['Organization']}</label>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <select class="col-md-12 form-control" style="height:30px" name="organizationId"
                                                        value="${cont[lang]['organizationId']}" required="required">
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Stratum Relations']}
                                        </label>
                                        <label type="text" name="organizationRelation">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Department Name']}
                                        </label>
                                        <label type="text" name="organizationName">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Country']}
                                        </label>
                                        <label type="text" name="organizationCountry">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Code']}
                                        </label>
                                        <label type="text" name="organizationCode">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Habitation']}
                                        </label>
                                        <label type="text" name="organizationHabitation">
                                        </label>
                                    </div>
                                    <div class="form-group">
                                        <label for="title">
                                            ${t[lang]['Organization Web URL']}
                                        </label>
                                        <label type="text" name="organizationUrl">
                                        </label>
                                    </div>
                                </div>
                            </div>
                            ## TODO: commonmaster 
                            <div class="form-group">
                                <label for="title">${t[lang]['Degree']}</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <select class="col-md-12 form-control" style="height:30px" name="positionId"
                                                value="${cont[lang]['positionId']}" required="required">
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="title">${t[lang]['Start Date']}</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <input type="date" class="StarDate form-control" name="startDate"
                                               value="${cont[lang]['startDate']}" required="required"/>
                                    </div>
                                </div>
                            </div>

                            <div class="form-group">
                                <label for="title">${t[lang]['End Date']}</label>
                                <div class="row">
                                    <div class="col-md-6">
                                        <input type="date" class="EndDate form-control" name="endDate"
                                               value="${cont[lang]['endDate']}" required="required"/>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </div>
                % endfor
                    <button style="margin-top:10px"  class="btn btn-success" id="save-data">
                        Save
                    </button>
            </div>
        </div>
    </div>
    <script type="text/javascript" src=${"/static/public/js/userAttribute.js" | webpack_asset}></script>
</%def>

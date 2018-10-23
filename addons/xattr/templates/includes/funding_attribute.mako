#coding=utf-8
<%page args="t"/>
<% langs=['ja', 'en'] %>

<input type="hidden" name="existing_fundings" id="existing_fundings" value="${content['fundings']}" />
% for lang in langs:
<div id="${lang}_fundingsExtensions" style="padding-top: 20px; margin-top: -20px;">
    <div id="manageFunding" style="border-top: 1px solid #ddd;">
        <h3 id="${lang}_fundings"> ${t[lang]['Fundings']}
            <a class="btn btn-success btn-sm m-l-md" data-toggle="modal" data-target="#${lang}_add-modal">
                <i class="fa fa-plus"></i> ${t[lang]['Add']}
            </a>
        </h3>
        <div id="${lang}_overview" data-bind="foreach: fundings">
            <div class="panel panel-default">
                <div class="well well-sm sort-handle">
                    <span data-bind="text: funderReference">Sample funding</span>
                    <div class="pull-right">
                        <th>
                            <button class="btn btn-danger btn-sm m-l-md" data-bind="click: $root.removeFunder" data-toggle="modal">
                                ${t[lang]['Remove']}
                            </button>
                            <button class="btn btn-success btn-sm m-l-md" data-bind="click: $root.showEditFunderForm" id="${lang}_edit-funding">
                                <i class="fa fa-edit"></i> ${t[lang]['Edit']}
                            </button>
                        </th>
                    </div>
                </div>
                <div id="funding" class="panel-body">
                    <table class="table">
                        <tr>
                            <th>${t[lang]['Funder Reference']}</th>
                            <td data-bind="text: funderReference">独立行政法人　日本学術振興会</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Funder Identifier']}</th>
                            <td data-bind="text: funderId"><a href="https://kaken.nii.ac.jp/ja/grant/KAKENHI-PROJECT-24500137/" target=_blank>24500137</a></td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Award Title']}</th>
                            <td data-bind="text: awardTitle">論文を構成するサプリメンタルデータを共有・再利用するための基盤技術開発</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Representative Researcher']}</th>
                            <td data-bind="text: applicants()[0].name()"><a href="https://nrid.nii.ac.jp/ja/nrid/1000050373379/" target=_blank>山地 一禎</a></td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Period']}</th>
                            <td data-bind="text: startDate() + ' - ' + endDate()">2012 - 2015</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Research Item']}</th>
                            <td data-bind="text: budgetCategory">基盤研究(C)</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Research Field']}</th>
                            <td data-bind="text: funderSubjectReachDegree">メディア情報学・データベース</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Research Organization']}</th>
                            <td data-bind="text: fundingProgramme">国立情報学研究所</td>
                        </tr>
                        <tr>
                            <th>${t[lang]['Status']}</th>
                            <td data-bind="text: status">完了（2014年度）</td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <div id="${lang}_funding-form" class="panel panel-default" data-bind="visible: addingFunder() || editingFunder() || fundings().length == 0">
        <span class="anchor"></span>
        <div class="panel-heading clearfix">
            <h3 class="panel-title" data-bind="text: funderInstance().funderReference">Sample funding</h3>
        </div>
        <div class="panel-body">
            <div class="form-group">
                <label for="title">${t[lang]['Funder Identifier']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: funderInstance().funderId" name="funderId">
                            <option>Funder IdentifierA</option>
                            <option>Funder IdentifierB</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Reference']}</label>
                <input class="form-control" data-bind="value: funderInstance().funderReference" name="funderReference" type="text">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Award Title']}</label>
                <input class="form-control" data-bind="value: funderInstance().awardTitle" name="awardTitle" type="text">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Budget Category']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: funderInstance().budgetCategory" name="budgetCategory">
                            <option>Budget CategoryA</option>
                            <option>Budget CategoryB</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funding Programme']}</label>
                <input class="form-control" data-bind="value: funderInstance().fundingProgramme" name="fundingProgramme" type="text" maxlength="200">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Status']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: funderInstance().status" name="status">
                            <option>StatusA</option>
                            <option>StatusB</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Available Funds']}</label>
                <div class="row">
                    <div class="col-md-6">
                        <select class="form-control" data-bind="value: funderInstance().availableFunds" name="availableFunds">
                            <option>Available FundsA</option>
                            <option>Available FundsB</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Start Date']}</label>
                <input type="date" class="StartDate form-control" data-bind="value: funderInstance().startDate" name="startDate"/>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['End Date']}</label>
                <input type="date" class="EndDate form-control" data-bind="value: funderInstance().endDate" name="endDate"/>
            </div>
            <div id="${lang}_applicant-list">
                <div class="panel panel-default" data-bind="foreach: funderInstance().applicants">
                    <div class="panel-heading clearfix">
                        <h3 class="panel-title">
                            <span>Sample Applicant</span>
                        </h3>
                        <a class="text-danger remove-applicant" data-bind="click: $root.funderInstance().removeApplicant" style="float:right">${t[lang]['Remove']}</a>
                    </div>
                    <div class="panel-body">
                        <div class="form-group">
                            <label for="title">${t[lang]['Name']}</label>
                            <div>
                                <div class="row funder_name_class">
                                    <div class="col-md-12">
                                        <input class="form-control" data-bind="value: name" name="name">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Alternate Name']}</label>
                            <input class="form-control" type="text"data-bind="value: alternativeName" name="alternativeName">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Organization']}</label>
                            <input class="form-control" type="text"data-bind="value: organization" name="organization">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Department']}</label>
                            <input class="form-control" type="text"data-bind="value: department" name="department">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Award Title']}</label>
                            <input class="form-control" type="text"data-bind="value: awardTitle" name="awardTitle">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Address']}</label>
                            <input class="form-control" type="text"data-bind="value: address" name="address">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Telephone']}</label>
                            <input class="form-control" type="text"data-bind="value: telephone" name="telephone">
                        </div>
                        <div class="form-group">
                            <label for="title">${t[lang]['Email']}</label>
                            <input class="form-control" type="text"data-bind="value: email" name="email">
                        </div>
                    </div>
                </div>
            </div>
            <div style="margin-bottom:20px">
                <a id="${lang}_add-applicant" data-bind="click: funderInstance().addApplicant" class="btn btn-success btn-sm m-l-md">
                    <i class="fa fa-plus">${t[lang]['Add']}</i>
                </a>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Subject Outline']}</label>
                <textarea name="funderSubjectOutline" data-bind="text: funderInstance().funderSubjectOutline" class="form-control col-md-12 element_margin_bottom"></textarea>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Subject Result Outline']}</label>
                <textarea name="funderSubjectResultOutline" data-bind="text: funderInstance().funderSubjectResultOutline" class="form-control col-md-12 element_margin_bottom"></textarea>
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Subject Reach Degree']}</label>
                <input class="form-control" type="text" data-bind="value: funderInstance().funderSubjectReachDegree" name="funderSubjectReachDegree">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Propulsion Scheme']}</label>
                <input class="form-control" type="text" data-bind="value: funderInstance().funderPropulsionScheme" name="funderPropulsionScheme">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Evaluation Mark']}</label>
                <input class="form-control" type="text" data-bind="value: funderInstance().funderEvaluationMark" name="funderEvaluationMark">
            </div>
            <div class="form-group">
                <label for="title">${t[lang]['Funder Evaluation Outline']}</label>
                <textarea name="funderEvaluationOutline" data-bind="text: funderInstance().funderEvaluationOutline" class="col-md-12 form-control" style="margin-bottom: 25px"></textarea>
            </div>
            <div class="form-group">
                <table class="table">
                    <thead>
                        <tr>
                            <th>${t[lang]['Payment Year']}</th>
                            <th>${t[lang]['Direct Costs']}</th>
                            <th>${t[lang]['Indirect Costs']}</th>
                            <th>
                                <a class="btn btn-success btn-sm m-l-md ${lang}_add-payment">
                                    <i class="fa fa-plus" data-bind="click: funderInstance().addPayment">${t[lang]['Add']}</i>
                                </a>
                            </th>
                        </tr>
                    </thead>
                    <tr>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                    <tbody class="costs-info-tbody" data-bind="foreach: funderInstance().payments" id="${lang}_payment-list">
                        <tr>
                            <td>
                                <input class="form-control col-md-3" data-bind="value: paymentYear" name="paymentYear" type="text">
                            </td>
                            <td>
                                <input class="form-control col-md-3" data-bind="value: directCosts" name="directCosts" type="text">
                            </td>
                            <td>
                                <input class="form-control col-md-3" data-bind="value: indirectCosts" name="indirectCosts" type="text">
                            </td>
                            <td>
                                <button class="btn btn-danger btn-sm m-l-md" data-bind="click: $root.funderInstance().removePayment" data-toggle="modal">
                                    ${t[lang]['Remove']}
                                </button>
                            </td>
                        </tr>
                    </tbody>
                    <tr>
                        <td>${t[lang]['Total Costs']}</td>
                        <td>
                            <span data-bind="text: funderInstance().totalDirectCosts"></span>
                        </td>
                        <td>
                            <span data-bind="text: funderInstance().totalIndirectCosts"></span>
                        </td>
                        <td></td>
                    </tr>
                </table>
            </div>
            <div class="form-group">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-danger close-funding" data-bind="click: cancelFunder">${t[lang]['Close']}</button>
                        <button class="btn btn-default close-funding" data-bind="click: cancelFunder">${t[lang]['Cancel']}</button>
                        <button class="btn btn-success" data-bind="click: saveFunder">${t[lang]['Save Changes']}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- addボタン押下時のモーダル -->
    <div class="modal fade" id="${lang}_add-modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                    <h4 class="modal-title" id="myModalLabel">Add New Fundings</h4>
                </div>
                <div class="modal-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Funder Identifier</th>
                                <th class="option">Funder Name</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><input class="form-control col-md-3" type="text"></td>
                                <td><input class="form-control col-md-3" type="text"></td>
                                <td class="option">
                                    <a href="#${lang}_funding-form" data-bind="click: showAddFunderForm" class="btn btn-success btn-sm m-l-md" id="${lang}_add-funding">
                                        <i class="fa fa-edit"></i> Add
                                    </a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-default" data-dismiss="modal" id="${lang}_cancel-funding">Cancel</button>
                </div>
            </div>
        </div>
    </div>
</div>

% endfor

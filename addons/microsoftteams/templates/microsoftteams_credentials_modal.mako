<div id="microsoftteamsCredentialsModal" class="modal fade">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">

            <div class="modal-header">
                <h3>${ _("Connect an Microsoft 365 Account")}</h3>
            </div>

            <form>
                <div class="modal-body">

                    <div class="row">
                        <div class="col-sm-6">
                            <div class="form-group">
                                <label for="microsoftteams_Tenant">${ _("Tenant ID")}</label>
                                <input class="form-control" data-bind="value: microsoftteamsTenant" id="microsoftteams_tenant" name="microsoftteams_Tenant" />
                            </div>
                            <div class="form-group">
                                <label for="microsoftteams_Client_Id">${ _("Application(Client) ID")}</label>
                                <input class="form-control" data-bind="value: microsoftteamsClientId" id="microsoftteams_client_id" name="microsoftteams_Client_Id" />
                            </div>
                            <div class="form-group">
                                <label for="microsoftteams_Client_Secret">${ _("Client Secret")}</label>
                                <input class="form-control" data-bind="value: microsoftteamsClientSecret" id="microsoftteams_client_secret" name="microsoftteams_Client_Secret" />
                            </div>
                        </div>
                    </div><!-- end row -->

                    <!-- Flashed Messages -->
                    <div class="help-block">
                        <p data-bind="html: message, attr: {class: messageClass}"></p>
                    </div>

                </div><!-- end modal-body -->

                <div class="modal-footer">

                    <a href="#" class="btn btn-default" data-bind="click: clearModal" data-dismiss="modal">${ _("Cancel")}</a>

                    <!-- Save Button -->
                    <button data-bind="click: connectAccount" class="btn btn-success">${ _("Save")}</button>

                </div><!-- end modal-footer -->

            </form>

        </div><!-- end modal-content -->
    </div>
</div>

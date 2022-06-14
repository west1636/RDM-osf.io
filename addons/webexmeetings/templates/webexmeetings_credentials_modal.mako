<div id="webexmeetingsCredentialsModal" class="modal fade">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">

            <div class="modal-header">
                <h3>${ _("Connect an Webex Meetings Account")}</h3>
            </div>

            <form>
                <div class="modal-body">

                    <div class="row">
                        <div class="col-sm-6">
                            <div class="form-group">
                                <label for="webexmeetings_Client_Id">${ _("Client ID")}</label>
                                    <!-- Link to Webex Meetings sign up page -->
                                    <a href="https://www.webex.com/"
                                       target="_blank" class="text-muted addon-external-link">
                                        ${_('(Get from Webex Meetings account%(externalLinkIcon)s)') % dict(externalLinkIcon='<i class="fa fa-external-link-square"></i>') | n}
                                    </a>
                                <input class="form-control" data-bind="value: webexmeetingsClientId" id="webexmeetings_client_id" name="webexmeetings_Client_Id" />
                            </div>
                            <div class="form-group">
                                <label for="webexmeetings_Client_Secret">${ _("Client Secret")}</label>
                                    <!-- Link to API token generation page -->
                                    <a href="https://www.webex.com/"
                                       target="_blank" class="text-muted addon-external-link">
                                        ${_('(Get from Webex Meetings account%(externalLinkIcon)s)') % dict(externalLinkIcon='<i class="fa fa-external-link-square"></i>') | n}
                                    </a>
                                <input class="form-control" data-bind="value: webexmeetingsClientSecret" id="webexmeetings_client_secret" name="webexmeetings_Client_Secret" />
                            </div>
                            <div class="form-group">
                                <label for="webexmeetings_OAuth_Url">${ _("OAuth Authorization URL")}</label>
                                    <!-- Link to API token generation page -->
                                    <a href="https://www.webex.com/"
                                       target="_blank" class="text-muted addon-external-link">
                                        ${_('(Get from Webex Meetings account%(externalLinkIcon)s)') % dict(externalLinkIcon='<i class="fa fa-external-link-square"></i>') | n}
                                    </a>
                                <input class="form-control" data-bind="value: webexmeetingsOAuthUrl" id="webexmeetings_oauth_url" name="webexmeetings_OAuth_Url" />
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

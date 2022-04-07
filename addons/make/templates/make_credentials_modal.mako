<div id="makeCredentialsModal" class="modal fade">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">

            <div class="modal-header">
                <h3>${ _("Connect an Make Account")}</h3>
            </div>

            <form>
                <div class="modal-body">

                    <div class="row">
                        <div class="col-sm-6">
                            <div class="form-group">
                                <label for="apiToken">${ _("API Token")}</label>
                                    <!-- Link to API token generation page -->
                                    <a href="https://apidocs.make.com/"
                                       target="_blank" class="text-muted addon-external-link">
                                        ${_('(Get from Make  %(externalLinkIcon)s)') % dict(externalLinkIcon='<i class="fa fa-external-link-square"></i>') | n}
                                    </a>
                                <input class="form-control" data-bind="value: makeApiToken" id="make_api_token" name="make_Api_Token" />
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

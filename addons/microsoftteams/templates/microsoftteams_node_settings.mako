<div id="${addon_short_name}Scope" class="scripted" >
    <div>
        <!-- Add credentials modal -->
        <%include file="microsoftteams_credentials_modal.mako"/>

        <h4 class="addon-title">
            <img class="addon-icon" src=${addon_icon_url}>
            ${addon_full_name}
            <small class="authorized-by">
                <span data-bind="if: nodeHasAuth">
                    ${_("authorized by %(ownerName)s") % dict(ownerName='<a data-bind="attr: {href: urls().owner}, text: ownerName"></a>') | n}
                    % if not is_registration:
                        <a data-bind="click: deauthorize, visible: validCredentials"
                            class="text-danger pull-right addon-auth">${_("Disconnect Account")}</a>
                    % endif
                </span>

             <!-- Import Access Token Button -->
                <span data-bind="if: showImport">
                    <a data-bind="click: importAuth" href="#" class="text-primary pull-right addon-auth">
                        ${_("Import Account from Profile")}
                    </a>
                </span>

                <!-- Loading Import Text -->
                <span data-bind="if: showLoading">
                    <p class="text-muted pull-right addon-auth">
                        ${_("Loading ...")}
                    </p>
                </span>

                <!-- Oauth Start Button -->
                <span data-bind="if: showTokenCreateButton">
                    <a href="#microsoftteamsCredentialsModal" data-toggle="modal" class="pull-right text-primary addon-auth">
                        ${_("Connect  Account")}
                    </a>
                </span>
            </small>
        </h4>
    </div>
</div>

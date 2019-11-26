<%inherit file="base.mako"/>
<%def name="title()">GakuNin RDM ${external_id_provider} ${ _("Login") } </%def>
<%def name="content()">
<h1 class="page-header text-center">GakuNin RDM ${external_id_provider} ${ _("Login | Register Email") } </h1>

<div class="row">
    ## Center the form
    <div class="col-md-6 col-md-offset-3">
        <p class='help'>
            ${ _("Please enter your email to finalize the login.") } 
            ${ _("If you already have a GakuNin RDM account, this will link your %(external_id_provider)s profile with GakuNin RDM.",external_id_provider=external_id_provider) }
            ${ _("If not, this will create a new account for you with your %(external_id_provider)s profile.",external_id_provider=external_id_provider) }
        </p>

        <form id='resendForm' method='POST' class='form' role='form'>
            <div class='form-group'>
                ${form.email(placeholder='${ _("Email address") }', autofocus=True, required=True) | unicode, n }
            </div>
            % if not auth_user_fullname:
                <div class='form-group'>
                    ${form.name(placeholder='${ _("Full name") }', autofocus=True, required='required') | unicode, n }
                </div>
            % endif
            <div class='form-group'>
                ${form.accepted_terms_of_service(required='required') | unicode, n }
                <label>${ _('I have read and agree to the .<a target="_blank" href="https://meatwiki.nii.ac.jp/confluence/pages/viewpage.action?pageId=32676419">Terms of Use.</a> and <a target="_blank" href="https://meatwiki.nii.ac.jp/confluence/pages/viewpage.action?pageId=32676422">Privacy Policy.</a>.') }</label>
            </div>
            <button type='submit' class='btn btn-primary'>${ _("Send") }</button>
            <a href='/logout' class='btn btn-danger'>${ _("Cancel") }</a>
        </form>
    </div>
</div>
</%def>

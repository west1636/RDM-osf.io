<%inherit file="base.mako"/>
<%def name="title()">${ _("Resend Confirmation Email") } </%def>
<%def name="content()">
<h1 class="page-header text-center">${ _("Resend Confirmation Email") } </h1>

<div class="row">
    ## Center the form
    <div class="col-md-6 col-md-offset-3">
        <p class='help'>${ _("Enter your email address and we'll resend your
        confirmation link.") } 
        </p>

        <form id='resendForm' method='POST' class='form' role='form'>
            <div class='form-group'>
                ${form.email(placeholder='Email address', autofocus=True) | unicode, n }
            </div>

            <button type='submit' class='btn btn-primary'>${ _("Send") } </button>
        </form>
    </div>
</div>
</%def>

from addons.webexmeetings.serializer import WebexMeetingsSerializer
from addons.webexmeetings import SHORT_NAME, FULL_NAME
from addons.webexmeetings import settings
from oauthlib.common import generate_token
from website.util import web_url_for
import urllib.parse
from framework.sessions import session
from osf.models.external import ExternalProvider

OAUTH2 = 2

class WebexMeetingsProvider(ExternalProvider):
    name = FULL_NAME
    short_name = SHORT_NAME
    serializer = WebexMeetingsSerializer

    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    auth_url_base = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/authorize')
    callback_url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/access_token')
    auto_refresh_url = callback_url

    response_type = 'code'
    scope_encoded = urllib.parse.quote(settings.WEBEX_API_SCOPE, safe="*")
    state = generate_token()

    def handle_callback(self, response):
        return {
            'provider_id': 'xxx',
            'display_name': 'yyy',
            'profile_url': 'zzz'
        }

    def fetch_access_token(self, force_refresh=False):
        self.refresh_oauth_key(force=force_refresh)
        return self.account.oauth_key

    def get_authorization_url(self, client_id):

        # create a dict on the session object if it's not already there
        if session.data.get('oauth_states') is None:
            session.data['oauth_states'] = {}

        assert self._oauth_version == OAUTH2

        response_type = 'code'
        redirect_uri = web_url_for(
            'oauth_callback',
            service_name=self.short_name,
            _absolute=True
        )
        redirect_uri_encoded = urllib.parse.quote(redirect_uri, safe="*")
        scope_encoded = urllib.parse.quote(settings.WEBEX_API_SCOPE, safe="*")
        state = generate_token()

        oauth_authorization_url = '{}?client_id={}&response_type={}&redirect_uri={}&scope={}&state={}'.format(settings.WEBEX_API_BASE_URL, client_id, response_type, redirect_uri_encoded, scope_encoded, state)

        # save state token to the session for confirmation in the callback
        session.data['oauth_states'][short_name] = {'state': state}

        session.save()
        return oauth_authorization_url

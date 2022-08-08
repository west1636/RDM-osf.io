import requests
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

    client_id = settings.WEBEX_MEETINGS_KEY
    client_secret = settings.WEBEX_MEETINGS_SECRET
    auth_url_base = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/authorize')
    callback_url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/access_token')
    auto_refresh_url = callback_url
    refresh_time = settings.REFRESH_TIME
    expiry_time = settings.EXPIRY_TIME

    def handle_callback(self, response):
        url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/people/me')
        requestToken = 'Bearer ' + response['access_token']
        requestHeaders = {
            'Authorization': requestToken,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=requestHeaders, timeout=60)
        info = response.json()
        return {
            'provider_id': info['id'],
            'display_name': info['displayName'],
        }

    def fetch_access_token(self, force_refresh=False):
        self.refresh_oauth_key(force=force_refresh)
        logger.info('{} refresh_oauth_key returns {}'.format(settings.WEBEX_MEETINGS, refreshed))
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

        oauth_authorization_url = '{}?client_id={}&response_type={}&redirect_uri={}&scope={}&state={}'.format(self.auth_url_base, client_id, response_type, redirect_uri_encoded, scope_encoded, state)

        # save state token to the session for confirmation in the callback
        session.data['oauth_states'][self.short_name] = {'state': state}

        session.save()
        return oauth_authorization_url

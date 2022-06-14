from addons.webexmeetings.serializer import WebexMeetingsSerializer
from addons.webexmeetings import SHORT_NAME, FULL_NAME
from addons.webexmeetings import settings
from osf.models.external import ExternalProvider

class WebexMeetingsProvider(ExternalProvider):
    name = FULL_NAME
    short_name = SHORT_NAME
    serializer = WebexMeetingsSerializer

    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    auth_url_base = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/authorize')
    callback_url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/access_token')
    auto_refresh_url = callback_url

    def handle_callback(self, response):
        return {
            'provider_id': 'xxx',
            'display_name': 'yyy',
            'profile_url': 'zzz'
        }

    def fetch_access_token(self, force_refresh=False):
        self.refresh_oauth_key(force=force_refresh)
        return self.account.oauth_key

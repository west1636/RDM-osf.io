from addons.webexmeetings.serializer import WebexMeetingsSerializer
from addons.webexmeetings import SHORT_NAME, FULL_NAME
from addons.webexmeetings import settings

class WebexMeetingsProvider(ExternalProvider):
    name = FULL_NAME
    short_name = SHORT_NAME
    serializer = WebexMeetingsSerializer

    callback_url = '{}{}'.format(settings.WEBEX_API_BASE_URL, 'v1/access_token')
    auto_refresh_url = callback_url

    def __init__(self, account=None):
        super(WebexMeetingsProvider, self).__init__()  # this does exactly nothing...
        # provide an unauthenticated session by default
        self.account = account

    def __repr__(self):
        return '<{name}: {status}>'.format(
            name=self.__class__.__name__,
            status=self.account.display_name if self.account else 'anonymous'
        )

    def fetch_access_token(self, force_refresh=False):
        self.refresh_oauth_key(force=force_refresh)
        return self.account.oauth_key

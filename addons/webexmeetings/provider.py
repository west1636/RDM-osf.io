from addons.webexmeetings.serializer import WebexMeetingsSerializer
from addons.webexmeetings import SHORT_NAME, FULL_NAME


class WebexMeetingsProvider(object):
    name = FULL_NAME
    short_name = SHORT_NAME
    serializer = WebexMeetingsSerializer

    def __init__(self, account=None):
        super(WebexMeetingsProvider, self).__init__()  # this does exactly nothing...
        # provide an unauthenticated session by default
        self.account = account

    def __repr__(self):
        return '<{name}: {status}>'.format(
            name=self.__class__.__name__,
            status=self.account.display_name if self.account else 'anonymous'
        )

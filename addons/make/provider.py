from addons.make.serializer import MakeSerializer
from addons.make import SHORT_NAME, FULL_NAME


class MakeProvider(object):
    name = FULL_NAME
    short_name = SHORT_NAME
    serializer = MakeSerializer

    def __init__(self, account=None):
        super(MakeProvider, self).__init__()  # this does exactly nothing...
        # provide an unauthenticated session by default
        self.account = account

    def __repr__(self):
        return '<{name}: {status}>'.format(
            name=self.__class__.__name__,
            status=self.account.display_name if self.account else 'anonymous'
        )

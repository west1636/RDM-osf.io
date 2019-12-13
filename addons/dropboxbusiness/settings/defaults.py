# OAuth app keys
DROPBOX_BUSINESS_FILEACCESS_KEY = None
DROPBOX_BUSINESS_FILEACCESS_SECRET = None
DROPBOX_BUSINESS_MANAGEMENT_KEY = None
DROPBOX_BUSINESS_MANAGEMENT_SECRET = None

DROPBOX_BUSINESS_AUTH_CSRF_TOKEN = 'dropboxbusiness-auth-csrf-token'

TEAM_FOLDER_NAME_PREFIX = 'GRDM-'
GROUP_NAME_PREFIX = 'GRDM-'

# Max file size permitted by frontend in megabytes
MAX_UPLOAD_SIZE = 150

EPPN_TO_EMAIL_MAP = {
    # e.g.
    # 'john@openidp.example.com': 'john.smith@mail.example.com',
}

EMAIL_TO_EPPN_MAP = dict(
    [(EPPN_TO_EMAIL_MAP[k], k) for k in EPPN_TO_EMAIL_MAP]
)

DEBUG_FILEACCESS_TOKEN = None
DEBUG_MANAGEMENT_TOKEN = None
DEBUG_ADMIN_DBMID = None

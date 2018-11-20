import logging
from osf.models import Guid


logger = logging.getLogger(__name__)

# userkey generation check
def generation_check(guid):
    from osf.models import RdmUserKey

    logger.info(' userkey_generation_check ')
    # no user_key_info
    if not RdmUserKey.objects.filter(guid=Guid.objects.get(_id=guid).object_id).exists():
        return False

    return True

# userkey generation
def generation(guid):
    logger.info('userkey_generation guid:' + guid)
    from api.base import settings as api_settings
    #from osf.models import RdmUserKey
    import os.path
    import subprocess
    from datetime import datetime
    import hashlib

    try:
        generation_date = datetime.now()
        generation_date_str = generation_date.strftime('%Y%m%d%H%M%S')
        generation_date_hash = hashlib.md5(generation_date_str).hexdigest()
        generation_pvt_key_name = api_settings.KEY_NAME_FORMAT.format(
            guid, generation_date_hash, api_settings.KEY_NAME_PRIVATE, api_settings.KEY_EXTENSION)
        generation_pub_key_name = api_settings.KEY_NAME_FORMAT.format(
            guid, generation_date_hash, api_settings.KEY_NAME_PUBLIC, api_settings.KEY_EXTENSION)
        # private key generation
        pvt_key_generation_cmd = [
            api_settings.OPENSSL_MAIN_CMD, api_settings.OPENSSL_OPTION_GENRSA,
            api_settings.OPENSSL_OPTION_OUT,
            os.path.join(api_settings.KEY_SAVE_PATH, generation_pvt_key_name),
            api_settings.KEY_BIT_VALUE
        ]

        pub_key_generation_cmd = [
            api_settings.OPENSSL_MAIN_CMD, api_settings.OPENSSL_OPTION_RSA,
            api_settings.OPENSSL_OPTION_IN,
            os.path.join(api_settings.KEY_SAVE_PATH, generation_pvt_key_name),
            api_settings.OPENSSL_OPTION_PUBOUT, api_settings.OPENSSL_OPTION_OUT,
            os.path.join(api_settings.KEY_SAVE_PATH, generation_pub_key_name)
        ]

        prc = subprocess.Popen(pvt_key_generation_cmd, shell=False,
                               stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        stdout_data, stderr_data = prc.communicate()

        prc = subprocess.Popen(pub_key_generation_cmd, shell=False,
                               stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)

        stdout_data, stderr_data = prc.communicate()

        pvt_userkey_info = create_rdmuserkey_info(
            Guid.objects.get(_id=guid).object_id, generation_pvt_key_name,
            api_settings.PRIVATE_KEY_VALUE, generation_date)

        pub_userkey_info = create_rdmuserkey_info(
            Guid.objects.get(_id=guid).object_id, generation_pub_key_name,
            api_settings.PUBLIC_KEY_VALUE, generation_date)

        pvt_userkey_info.save()
        pub_userkey_info.save()

    except Exception as error:
        logger.exception(error)

def create_rdmuserkey_info(user_id, key_name, key_kind, date):
    from osf.models import RdmUserKey

    userkey_info = RdmUserKey()
    userkey_info.guid = user_id
    userkey_info.key_name = key_name
    userkey_info.key_kind = key_kind
    userkey_info.created_time = date

    return userkey_info

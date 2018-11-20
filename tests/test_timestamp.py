import datetime
import os
import pytz
import shutil
from api.base import settings as api_settings
from api_tests.utils import create_test_file
from framework.auth import Auth
from nose import tools as nt
from osf.models import RdmUserKey, RdmFileTimestamptokenVerifyResult, Guid
from osf_tests.factories import ProjectFactory, AuthUserFactory
from tests.base import ApiTestCase, OsfTestCase
from website.util.timestamp import (
    AddTimestamp, TimeStampTokenVerifyCheck,
    userkey_generation, userkey_generation_check
)


class TestAddTimestamp(ApiTestCase):
    def setUp(self):
        super(TestAddTimestamp, self).setUp()

        self.project = ProjectFactory()
        self.node = self.project
        self.user = self.project.creator
        self.node_settings = self.project.get_addon('osfstorage')
        self.auth_obj = Auth(user=self.project.creator)
        userkey_generation(self.user._id)

        # Refresh records from database; necessary for comparing dates
        self.project.reload()
        self.user.reload()

    def tearDown(self):
        from api.base import settings as api_settings
        from osf.models import RdmUserKey

        super(TestAddTimestamp, self).tearDown()
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        self.user.delete()

        rdmuserkey_pvt_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PRIVATE_KEY_VALUE)
        pvt_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pvt_key.key_name)
        os.remove(pvt_key_path)
        rdmuserkey_pvt_key.delete()

        rdmuserkey_pub_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PUBLIC_KEY_VALUE)
        pub_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pub_key.key_name)
        os.remove(pub_key_path)
        rdmuserkey_pub_key.delete()

    def test_add_timestamp(self):
        ## create file_node
        filename = 'test_file_add_timestamp'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        download_file_path = os.path.join(tmp_dir, filename)
        with open(download_file_path, 'wb') as fout:
            fout.write('test_file_add_timestamp_context')

        ## add timestamp
        addTimestamp = AddTimestamp()
        ret = addTimestamp.add_timestamp(self.user._id, file_node._id, self.node._id, 'osfstorage', os.path.join('/', filename), download_file_path, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check add_timestamp func response
        nt.assert_equal(ret['verify_result'], 1)
        nt.assert_equal(ret['verify_result_title'], 'OK')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 1)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)


class TestTimeStampTokenVerifyCheck(ApiTestCase):
    def setUp(self):
        super(TestTimeStampTokenVerifyCheck, self).setUp()

        self.project = ProjectFactory()
        self.node = self.project
        self.user = self.project.creator
        self.auth_obj = Auth(user=self.project.creator)
        userkey_generation(self.user._id)

        # Refresh records from database; necessary for comparing dates
        self.project.reload()
        self.user.reload()

    def tearDown(self):
        from osf.models import RdmUserKey

        super(TestTimeStampTokenVerifyCheck, self).tearDown()
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        self.user.delete()

        rdmuserkey_pvt_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PRIVATE_KEY_VALUE)
        pvt_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pvt_key.key_name)
        os.remove(pvt_key_path)
        rdmuserkey_pvt_key.delete()

        rdmuserkey_pub_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PUBLIC_KEY_VALUE)
        pub_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pub_key.key_name)
        os.remove(pub_key_path)
        rdmuserkey_pub_key.delete()

    def test_timestamp_check_return_status_1(self):
        """
        TIME_STAMP_TOKEN_CHECK_SUCCESS = 1
        TIME_STAMP_TOKEN_CHECK_SUCCESS_MSG = 'OK'
        """
        provider = 'osfstorage'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        with open(tmp_file, 'wb') as fout:
            fout.write('test_file_timestamp_check_context')

        ## add timestamp
        addTimestamp = AddTimestamp()
        addTimestamp.add_timestamp(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 1)
        nt.assert_equal(ret['verify_result_title'], 'OK')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 1)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)

    def test_timestamp_check_return_status_2(self):
        """
        [IN & Testdata]
         RdmFileTimestamptokenVerifyResult : Exist & RdmFileTimestamptokenVerifyResult.timestamp_token != null
         provider = 's3'
         * File(tmp_file) update from outside the system
        [OUT]
          TIME_STAMP_TOKEN_CHECK_NG = 2
          TIME_STAMP_TOKEN_CHECK_NG_MSG = 'NG'
        """
        provider = 's3'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        with open(tmp_file, 'wb') as fout:
            fout.write('test_timestamp_check_return_status_2.test_file_context')

        ## add timestamp
        addTimestamp = AddTimestamp()
        addTimestamp.add_timestamp(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)

        ## File(tmp_file) update from outside the system
        with open(tmp_file, 'wb') as fout:
            fout.write('test_timestamp_check_return_status_2.test_file_context...File(tmp_file) update from outside the system.')

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 2)
        nt.assert_equal(ret['verify_result_title'], 'NG')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 2)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)

    def test_timestamp_check_return_status_3(self):
        """
        [IN & Testdata]
         BaseFileNode : Exist
         RdmFileTimestamptokenVerifyResult : None
         provider = 'osfstorage'
        [OUT]
         TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND = 3
         TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG = 'TST missing(Unverify)'
        """
        provider = 'osfstorage'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        with open(tmp_file, 'wb') as fout:
            fout.write('test_file_timestamp_check_context')

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 3)
        nt.assert_equal(ret['verify_result_title'], 'TST missing(Unverify)')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 3)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)

    def test_timestamp_check_return_status_4(self):
        """
        [IN & Testdata]
         BaseFileNode : Exist & BaseFileNode.is_deleted = False
         RdmFileTimestamptokenVerifyResult : Exist & RdmFileTimestamptokenVerifyResult.timestamp_token = null
         provider = 'osfstorage'
        [OUT]
         TIME_STAMP_TOKEN_NO_DATA = 4
         TIME_STAMP_TOKEN_NO_DATA_MSG = 'TST missing(Retrieving Failed)'
        """
        provider = 'osfstorage'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        #with open(tmp_file, 'wb') as fout:
        #    fout.write('test_file_timestamp_check_context')

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 4)
        nt.assert_equal(ret['verify_result_title'], 'TST missing(Retrieving Failed)')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 4)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)

    def test_timestamp_check_return_status_5(self):
        """
        [IN & Testdata]
         BaseFileNode : Exist & BaseFileNode.is_deleted = True
         RdmFileTimestamptokenVerifyResult : None
         provider = 'osfstorage'
        [OUT]
         FILE_NOT_EXISTS = 5
         FILE_NOT_EXISTS_MSG = 'FILE missing'
        """
        provider = 'osfstorage'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)
        file_node.delete()

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        #with open(tmp_file, 'wb') as fout:
        #    fout.write('test_file_timestamp_check_context')

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 5)
        nt.assert_equal(ret['verify_result_title'], 'FILE missing')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 5)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)

    def test_timestamp_check_return_status_6(self):
        """
        [IN & Testdata]
         BaseFileNode : Exist & BaseFileNode.is_deleted = True
         RdmFileTimestamptokenVerifyResult : Exist & RdmFileTimestamptokenVerifyResult.timestamp_token = null
         provider = 'osfstorage'
        [OUT]
         FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND = 6
         FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG = 'FILE missing(Unverify)'
        """
        provider = 'osfstorage'
        self.node_settings = self.project.get_addon(provider)

        ## create file_node(BaseFileNode record)
        filename = 'test_file_timestamp_check'
        file_node = create_test_file(node=self.node, user=self.user, filename=filename)
        file_node.delete()

        ## create tmp_dir
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(self.user._id, file_node._id, current_datetime_str)
        os.mkdir(tmp_dir)

        ## create tmp_file (file_node)
        tmp_file = os.path.join(tmp_dir, filename)
        #with open(tmp_file, 'wb') as fout:
        #    fout.write('test_file_timestamp_check_context')

        ## verify timestamptoken
        verifyCheck = TimeStampTokenVerifyCheck()
        verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        ret = verifyCheck.timestamp_check(self.user._id, file_node._id, self.node._id, provider, os.path.join('/', filename), tmp_file, tmp_dir)
        shutil.rmtree(tmp_dir)

        ## check timestamp_check func response
        nt.assert_equal(ret['verify_result'], 6)
        nt.assert_equal(ret['verify_result_title'], 'FILE missing(Unverify)')

        ## check rdmfiletimestamptokenverifyresult record
        rdmfiletimestamptokenverifyresult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_node._id)
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        nt.assert_equal(rdmfiletimestamptokenverifyresult.inspection_result_status, 6)
        nt.assert_equal(rdmfiletimestamptokenverifyresult.validation_user, osfuser_id)


class TestRdmUserKey(OsfTestCase):
    def setUp(self):
        super(TestRdmUserKey, self).setUp()
        self.user = AuthUserFactory()

    def tearDown(self):
        super(TestRdmUserKey, self).tearDown()
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id

        key_exists_check = userkey_generation_check(self.user._id)
        if key_exists_check:
            rdmuserkey_pvt_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PRIVATE_KEY_VALUE)
            pvt_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pvt_key.key_name)
            os.remove(pvt_key_path)
            rdmuserkey_pvt_key.delete()

            rdmuserkey_pub_key = RdmUserKey.objects.get(guid=osfuser_id, key_kind=api_settings.PUBLIC_KEY_VALUE)
            pub_key_path = os.path.join(api_settings.KEY_SAVE_PATH, rdmuserkey_pub_key.key_name)
            os.remove(pub_key_path)
            rdmuserkey_pub_key.delete()
        self.user.delete()

    def test_userkey_generation_check_return_true(self):
        userkey_generation(self.user._id)
        nt.assert_true(userkey_generation_check(self.user._id))

    def test_userkey_generation_check_return_false(self):
        nt.assert_false(userkey_generation_check(self.user._id))

    def test_userkey_generation(self):
        osfuser_id = Guid.objects.get(_id=self.user._id).object_id
        userkey_generation(self.user._id)

        rdmuserkey_pvt_key = RdmUserKey.objects.filter(guid=osfuser_id, key_kind=api_settings.PRIVATE_KEY_VALUE)
        nt.assert_equal(rdmuserkey_pvt_key.count(), 1)

        rdmuserkey_pub_key = RdmUserKey.objects.filter(guid=osfuser_id, key_kind=api_settings.PUBLIC_KEY_VALUE)
        nt.assert_equal(rdmuserkey_pub_key.count(), 1)

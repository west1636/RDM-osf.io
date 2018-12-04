# -*- coding: utf-8 -*-

from __future__ import absolute_import

from api.base import settings as api_settings
from api.base.rdmlogger import RdmLogger, rdmlog
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from osf.models import (
    AbstractNode, BaseFileNode, Guid, RdmFileTimestamptokenVerifyResult, RdmUserKey,
    OSFUser
)
from urllib3.util.retry import Retry
from website import util
from website import settings
import datetime
import hashlib
import logging
import os
import pytz
import requests
import shutil
import subprocess
import time
import traceback


logger = logging.getLogger(__name__)

RESULT_MESSAGE = {
    api_settings.TIME_STAMP_TOKEN_CHECK_NG:
        api_settings.TIME_STAMP_TOKEN_CHECK_NG_MSG,  # 'NG'
    api_settings.TIME_STAMP_TOKEN_NO_DATA:
        api_settings.TIME_STAMP_TOKEN_NO_DATA_MSG,  # 'TST missing(Retrieving Failed)'
    api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND:
        api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG,  # 'TST missing(Unverify)'
    api_settings.FILE_NOT_EXISTS:
        api_settings.FILE_NOT_EXISTS_MSG  # 'FILE missing'
}

def get_error_list(pid):
    '''
    Retrieve from the database the list of all timestamps that has an error.
    '''
    data_list = RdmFileTimestamptokenVerifyResult.objects.filter(project_id=pid).order_by('provider', 'path')
    provider_error_list = []
    provider = None
    error_list = []

    for data in data_list:
        if data.inspection_result_status == api_settings.TIME_STAMP_TOKEN_CHECK_SUCCESS:
            data.inspection_result_status = api_settings.TIME_STAMP_TOKEN_CHECK_NG
            # continue

        if not provider:
            provider = data.provider
        elif provider != data.provider:
            provider_error_list.append({'provider': provider, 'error_list': error_list})
            provider = data.provider
            error_list = []

        if data.inspection_result_status in RESULT_MESSAGE:
            verify_result_title = RESULT_MESSAGE[data.inspection_result_status]
        else:  # 'FILE missing(Unverify)'
            verify_result_title = \
                api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG

        if not data.update_user:
            operator_user = OSFUser.objects.get(id=data.create_user)
            operator_date = data.create_date.strftime('%Y/%m/%d %H:%M:%S')
        else:
            operator_user = OSFUser.objects.get(id=data.update_user)
            operator_date = data.update_date.strftime('%Y/%m/%d %H:%M:%S')

        if provider == 'osfstorage':
            base_file_data = BaseFileNode.objects.get(_id=data.file_id)
            error_info = {
                'file_name': base_file_data.name,
                'file_path': data.path,
                'file_kind': 'file',
                'project_id': data.project_id,
                'file_id': data.file_id,
                'version': base_file_data.current_version_number,
                'operator_user': operator_user.fullname,
                'operator_user_id': operator_user._id,
                'operator_date': operator_date,
                'verify_result_title': verify_result_title,
                'creator_name': base_file_data.versions.filter().last().creator.fullname,
                'creator_email': base_file_data.versions.filter().last().creator.username,
                'creator_id': base_file_data.versions.filter().last().creator.id,
                'creator_institution': base_file_data.versions.filter().last().creator.affiliated_institutions.first()
            }
        else:
            file_name = os.path.basename(data.path)
            error_info = {
                'file_name': file_name,
                'file_path': data.path,
                'file_kind': 'file',
                'project_id': data.project_id,
                'file_id': data.file_id,
                'version': '',
                'operator_user': operator_user.fullname,
                'operator_user_id': operator_user._id,
                'operator_date': operator_date,
                'verify_result_title': verify_result_title
            }
        error_list.append(error_info)

    if error_list:
        provider_error_list.append({'provider': provider, 'error_list': error_list})

    return provider_error_list

def get_full_list(uid, pid, node):
    '''
    Get a full list of timestamps from all files uploaded to a storage.
    '''
    user_info = OSFUser.objects.get(id=uid)
    cookie = user_info.get_or_create_cookie()

    api_url = util.api_v2_url('nodes/{}/files'.format(pid))
    headers = {'content-type': 'application/json'}
    cookies = {settings.COOKIE_NAME: cookie}

    file_res = requests.get(api_url, headers=headers, cookies=cookies)
    provider_json_res = file_res.json()
    file_res.close()
    provider_list = []

    for provider_data in provider_json_res['data']:
        waterbutler_meta_url = util.waterbutler_api_url_for(
            pid,
            provider_data['attributes']['provider'],
            '/',
            **dict({'meta=&_': int(time.mktime(datetime.datetime.now().timetuple()))})
        )
        waterbutler_json_res = None
        waterbutler_res = requests.get(waterbutler_meta_url, headers=headers, cookies=cookies)
        waterbutler_json_res = waterbutler_res.json()
        waterbutler_res.close()

        file_list = []
        child_file_list = []
        for file_data in waterbutler_json_res['data']:
            if file_data['attributes']['kind'] == 'folder':
                child_file_list.extend(
                    waterbutler_folder_file_info(
                        pid,
                        provider_data['attributes']['provider'],
                        file_data['attributes']['path'],
                        node, cookies, headers
                    )
                )
            else:
                file_info = None
                basefile_node = BaseFileNode.resolve_class(
                    provider_data['attributes']['provider'],
                    BaseFileNode.FILE
                ).get_or_create(
                    node,
                    file_data['attributes']['path']
                )
                basefile_node.save()
                if provider_data['attributes']['provider'] == 'osfstorage':
                    file_info = {
                        'file_name': file_data['attributes']['name'],
                        'file_path': file_data['attributes']['materialized'],
                        'file_kind': file_data['attributes']['kind'],
                        'file_id': basefile_node._id,
                        'version': file_data['attributes']['extra']['version']
                    }
                else:
                    file_info = {
                        'file_name': file_data['attributes']['name'],
                        'file_path': file_data['attributes']['materialized'],
                        'file_kind': file_data['attributes']['kind'],
                        'file_id': basefile_node._id,
                        'version': ''
                    }
                if file_info:
                    file_list.append(file_info)

        file_list.extend(child_file_list)

        if file_list:
            provider_files = {
                'provider': provider_data['attributes']['provider'],
                'provider_file_list': file_list
            }
            provider_list.append(provider_files)

    return provider_list

def check_file_timestamp(uid, node, data):
    user = OSFUser.objects.get(id=uid)
    cookie = user.get_or_create_cookie()
    headers = {'content-type': 'application/json'}
    cookies = {settings.COOKIE_NAME: cookie}
    url = None
    tmp_dir = None
    result = None

    try:
        file_node = BaseFileNode.objects.get(_id=data['file_id'])
        if data['provider'] == 'osfstorage':
            url = file_node.generate_waterbutler_url(
                action='download',
                version=data['version'],
                direct=None, _internal=False
            )

        else:
            url = file_node.generate_waterbutler_url(
                action='download',
                direct=None, _internal=False
            )

        res = requests.get(url, headers=headers, cookies=cookies)
        current_datetime = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S%f')
        tmp_dir = 'tmp_{}_{}_{}'.format(user._id, file_node._id, current_datetime_str)

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        download_file_path = os.path.join(tmp_dir, data['file_name'])
        with open(download_file_path, 'wb') as fout:
            fout.write(res.content)
            res.close()

        verify_check = TimeStampTokenVerifyCheck()
        result = verify_check.timestamp_check(
            user._id, data['file_id'],
            node._id, data['provider'], data['file_path'], download_file_path, tmp_dir
        )

        shutil.rmtree(tmp_dir)
        return result

    except Exception as err:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        logger.exception(err)
        raise

def add_token(uid, node, data):
    user = OSFUser.objects.get(id=uid)
    cookie = user.get_or_create_cookie()
    headers = {'content-type': 'application/json'}
    cookies = {settings.COOKIE_NAME: cookie}
    url = None
    tmp_dir = None

    try:
        file_node = BaseFileNode.objects.get(_id=data['file_id'])
        if data['provider'] == 'osfstorage':
            url = file_node.generate_waterbutler_url(
                action='download',
                version=data['version'],
                direct=None, _internal=False
            )
        else:
            url = file_node.generate_waterbutler_url(
                action='download',
                direct=None, _internal=False
            )

        # Request To Download File
        res = requests.get(url, headers=headers, cookies=cookies)
        tmp_dir = 'tmp_{}'.format(user._id)
        count = 1
        while os.path.exists(tmp_dir):
            count += 1
            tmp_dir = 'tmp_{}_{}'.format(user._id, count)
        os.mkdir(tmp_dir)
        download_file_path = os.path.join(tmp_dir, data['file_name'])
        with open(download_file_path, 'wb') as fout:
            fout.write(res.content)
            res.close()

        addTimestamp = AddTimestamp()
        result = addTimestamp.add_timestamp(
            user._id, data['file_id'],
            node._id, data['provider'], data['file_path'],
            download_file_path, tmp_dir
        )

        shutil.rmtree(tmp_dir)
        return result

    except Exception as err:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        logger.exception(err)
        raise

def waterbutler_folder_file_info(pid, provider, path, node, cookies, headers):
    # get waterbutler folder file
    if provider == 'osfstorage':
        waterbutler_meta_url = util.waterbutler_api_url_for(
            pid, provider,
            '/' + path,
            **dict({'meta=&_': int(time.mktime(datetime.datetime.now().timetuple()))})
        )
    else:
        waterbutler_meta_url = util.waterbutler_api_url_for(
            pid, provider,
            path,
            **dict({'meta=&_': int(time.mktime(datetime.datetime.now().timetuple()))})
        )

    waterbutler_res = requests.get(waterbutler_meta_url, headers=headers, cookies=cookies)
    waterbutler_json_res = waterbutler_res.json()
    waterbutler_res.close()
    file_list = []
    child_file_list = []
    for file_data in waterbutler_json_res['data']:
        if file_data['attributes']['kind'] == 'folder':
            child_file_list.extend(waterbutler_folder_file_info(
                pid, provider, file_data['attributes']['path'],
                node, cookies, headers))
        else:
            basefile_node = BaseFileNode.resolve_class(
                provider,
                BaseFileNode.FILE
            ).get_or_create(
                node,
                file_data['attributes']['path']
            )
            basefile_node.save()
            if provider == 'osfstorage':
                file_info = {
                    'file_name': file_data['attributes']['name'],
                    'file_path': file_data['attributes']['materialized'],
                    'file_kind': file_data['attributes']['kind'],
                    'file_id': basefile_node._id,
                    'version': file_data['attributes']['extra']['version']
                }
            else:
                file_info = {
                    'file_name': file_data['attributes']['name'],
                    'file_path': file_data['attributes']['materialized'],
                    'file_kind': file_data['attributes']['kind'],
                    'file_id': basefile_node._id,
                    'version': ''
                }

            file_list.append(file_info)

    file_list.extend(child_file_list)
    return file_list

def userkey_generation_check(guid):
    return RdmUserKey.objects.filter(guid=Guid.objects.get(_id=guid).object_id).exists()

def userkey_generation(guid):
    logger.info('userkey_generation guid:' + guid)

    try:
        generation_date = datetime.datetime.now()
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

        prc = subprocess.Popen(
            pvt_key_generation_cmd, shell=False, stdin=subprocess.PIPE,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        stdout_data, stderr_data = prc.communicate()

        prc = subprocess.Popen(
            pub_key_generation_cmd, shell=False, stdin=subprocess.PIPE,
            stderr=subprocess.PIPE, stdout=subprocess.PIPE)

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
        raise

def create_rdmuserkey_info(user_id, key_name, key_kind, date):
    userkey_info = RdmUserKey()
    userkey_info.guid = user_id
    userkey_info.key_name = key_name
    userkey_info.key_kind = key_kind
    userkey_info.created_time = date
    return userkey_info


class AddTimestamp:
    #①鍵情報テーブルから操作ユーザに紐づく鍵情報を取得する
    def get_userkey(self, user_id):
        userKey = RdmUserKey.objects.get(guid=user_id, key_kind=api_settings.PUBLIC_KEY_VALUE)
        return userKey.key_name

    #②ファイル情報 + 鍵情報をハッシュ化したタイムスタンプリクエスト（tsq）を生成する
    def get_timestamp_request(self, file_name):
        cmd = [
            api_settings.OPENSSL_MAIN_CMD, api_settings.OPENSSL_OPTION_TS,
            api_settings.OPENSSL_OPTION_QUERY, api_settings.OPENSSL_OPTION_DATA,
            file_name, api_settings.OPENSSL_OPTION_CERT, api_settings.OPENSSL_OPTION_SHA512
        ]
        process = subprocess.Popen(
            cmd, shell=False, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout_data, stderr_data = process.communicate()
        return stdout_data

    #③tsqをTSAに送信してタイムスタンプトークン（tsr）を受け取る
    def get_timestamp_response(self, file_name, ts_request_file, key_file):
        res_content = None
        try:
            retries = Retry(
                total=api_settings.REQUEST_TIME_OUT, backoff_factor=1,
                status_forcelist=api_settings.ERROR_HTTP_STATUS)
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

            res = requests.post(
                api_settings.TIME_STAMP_AUTHORITY_URL, headers=api_settings.REQUEST_HEADER,
                data=ts_request_file, stream=True)
            res_content = res.content
            res.close()

        except Exception as ex:
            logger.exception(ex)
            traceback.print_exc()
            res_content = None

        return res_content

    #④データの取得
    def get_data(self, file_id, project_id, provider, path):
        try:
            res = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_id)
        except ObjectDoesNotExist:
            res = None
        return res

    #⑤ファイルタイムスタンプトークン情報テーブルに登録。
    def timestamptoken_register(
            self, file_id, project_id, provider, path, key_file,
            tsa_response, user_id, verify_data):
        try:
            # データが登録されていない場合
            if not verify_data:
                verify_data = RdmFileTimestamptokenVerifyResult()
                verify_data.key_file_name = key_file
                verify_data.file_id = file_id
                verify_data.project_id = project_id
                verify_data.provider = provider
                verify_data.path = path
                verify_data.timestamp_token = tsa_response
                verify_data.inspection_result_status = api_settings.TIME_STAMP_TOKEN_UNCHECKED
                verify_data.create_user = user_id
                verify_data.create_date = datetime.datetime.now()

            # データがすでに登録されている場合
            else:
                verify_data.key_file_name = key_file
                verify_data.timestamp_token = tsa_response
                verify_data.update_user = user_id
                verify_data.update_date = datetime.datetime.now()

            verify_data.save()
        except Exception as ex:
            logger.exception(ex)

    #⑥メイン処理
    def add_timestamp(self, guid, file_id, project_id, provider, path, file_name, tmp_dir):
        # guid から user_idを取得する
        user_id = Guid.objects.get(_id=guid).object_id

        # ユーザ鍵情報を取得する。
        key_file_name = self.get_userkey(user_id)

        # タイムスタンプリクエスト生成
        tsa_request = self.get_timestamp_request(file_name)

        # タイムスタンプトークン取得
        tsa_response = self.get_timestamp_response(file_name, tsa_request, key_file_name)

        # 検証データ存在チェック
        verify_data = self.get_data(file_id, project_id, provider, path)

        # 検証結果テーブルに登録する。
        self.timestamptoken_register(
            file_id, project_id, provider, path, key_file_name, tsa_response,
            user_id, verify_data)

        # （共通処理）タイムスタンプ検証処理の呼び出し
        return TimeStampTokenVerifyCheck().timestamp_check(
            guid, file_id, project_id, provider, path, file_name, tmp_dir)


class TimeStampTokenVerifyCheck:
    # abstractNodeデータ取得
    def get_abstractNode(self, node_id):
        # プロジェクト名取得
        try:
            abstractNode = AbstractNode.objects.get(id=node_id)
        except Exception as err:
            logging.exception(err)
            abstractNode = None

        return abstractNode

    # 検証結果データ取得
    def get_verifyResult(self, file_id, project_id, provider, path):
        # 検証結果取得
        try:
            if RdmFileTimestamptokenVerifyResult.objects.filter(file_id=file_id).exists():
                verifyResult = RdmFileTimestamptokenVerifyResult.objects.get(file_id=file_id)
            else:
                verifyResult = None

        except Exception as err:
            logging.exception(err)
            verifyResult = None

        return verifyResult

    # baseFileNodeデータ取得
    def get_baseFileNode(self, file_id):
        # ファイル取得
        try:
            baseFileNode = BaseFileNode.objects.get(_id=file_id)
        except Exception as err:
            logging.exception(err)
            baseFileNode = None

        return baseFileNode

    # baseFileNodeのファイルパス取得
    def get_filenameStruct(self, fsnode, fname):
        try:
            if fsnode.parent is not None:
                fname = self.get_filenameStruct(fsnode.parent, fname) + '/' + fsnode.name
            else:
                fname = fsnode.name
        except Exception as err:
            logging.exception(err)

        return fname

    def create_rdm_filetimestamptokenverify(
            self, file_id, project_id, provider, path, inspection_result_status, userid):

        userKey = RdmUserKey.objects.get(guid=userid, key_kind=api_settings.PUBLIC_KEY_VALUE)
        create_data = RdmFileTimestamptokenVerifyResult()
        create_data.file_id = file_id
        create_data.project_id = project_id
        create_data.provider = provider
        create_data.key_file_name = userKey.key_name
        create_data.path = path
        create_data.inspection_result_status = inspection_result_status
        create_data.validation_user = userid
        create_data.validation_date = timezone.now()
        create_data.create_user = userid
        create_data.create_date = timezone.now()
        return create_data

    # タイムスタンプトークンチェック
    def timestamp_check(self, guid, file_id, project_id, provider, path, file_name, tmp_dir):
        userid = Guid.objects.get(_id=guid).object_id

        # 検証結果取得
        verifyResult = self.get_verifyResult(file_id, project_id, provider, path)

        ret = 0
        operator_user = None
        operator_date = None
        verify_result_title = None

        try:
            # ファイル情報と検証結果のタイムスタンプ未登録確認
            if provider == 'osfstorage':
                # ファイル取得
                baseFileNode = self.get_baseFileNode(file_id)
                if baseFileNode.is_deleted and not verifyResult:
                    # ファイルが削除されていて検証結果がない場合
                    ret = api_settings.FILE_NOT_EXISTS
                    verify_result_title = api_settings.FILE_NOT_EXISTS_MSG  # 'FILE missing'
                    verifyResult = self.create_rdm_filetimestamptokenverify(
                        file_id, project_id, provider, path, ret, userid)

                elif baseFileNode.is_deleted and verifyResult and not verifyResult.timestamp_token:
                    # ファイルが存在しなくてタイムスタンプトークンが未検証がない場合
                    verifyResult.inspection_result_status = \
                        api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND
                    verifyResult.validation_user = userid
                    verifyResult.validation_date = datetime.datetime.now()
                    ret = api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND
                    # 'FILE missing(Unverify)'
                    verify_result_title = \
                        api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG

                elif baseFileNode.is_deleted and verifyResult:
                    # ファイルが削除されていて、検証結果テーブルにレコードが存在する場合
                    verifyResult.inspection_result_status = \
                        api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND
                    verifyResult.validation_user = userid
                    verifyResult.validation_date = datetime.datetime.now()
                    # ファイルが削除されていて検証結果があり場合、検証結果テーブルを更新する。
                    ret = api_settings.FILE_NOT_EXISTS_TIME_STAMP_TOKEN_NO_DATA

                elif not baseFileNode.is_deleted and not verifyResult:
                    # ファイルは存在し、検証結果のタイムスタンプが未登録の場合は更新する。
                    ret = api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND
                    # 'TST missing(Unverify)'
                    verify_result_title = \
                        api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG
                    verifyResult = self.create_rdm_filetimestamptokenverify(
                        file_id, project_id, provider, path, ret, userid)

                elif not baseFileNode.is_deleted and not verifyResult.timestamp_token:
                    # ファイルは存在し、検証結果のタイムスタンプが未登録の場合は更新する。
                    verifyResult.inspection_result_status = api_settings.TIME_STAMP_TOKEN_NO_DATA
                    verifyResult.validation_user = userid
                    verifyResult.validation_date = datetime.datetime.now()
                    # ファイルが削除されていて検証結果があり場合、検証結果テーブルを更新する。
                    ret = api_settings.TIME_STAMP_TOKEN_NO_DATA
                    # 'TST missing(Retrieving Failed)'
                    verify_result_title = api_settings.TIME_STAMP_TOKEN_NO_DATA_MSG

            else:
                if not verifyResult:
                    # ファイルが存在せず、検証結果がない場合
                    ret = api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND
                    # 'TST missing(Unverify)'
                    verify_result_title = api_settings.TIME_STAMP_TOKEN_CHECK_FILE_NOT_FOUND_MSG
                    verifyResult = self.create_rdm_filetimestamptokenverify(
                        file_id, project_id, provider, path, ret, userid)

                elif not verifyResult.timestamp_token:
                    verifyResult.inspection_result_status = api_settings.TIME_STAMP_TOKEN_NO_DATA
                    verifyResult.validation_user = userid
                    verifyResult.validation_date = datetime.datetime.now()
                    # ファイルが削除されていて検証結果があり場合、検証結果テーブルを更新する。
                    ret = api_settings.TIME_STAMP_TOKEN_NO_DATA
                    # 'TST missing(Retrieving Failed)'
                    verify_result_title = api_settings.TIME_STAMP_TOKEN_NO_DATA_MSG

            if ret == 0:
                timestamptoken_file = guid + '.tsr'
                timestamptoken_file_path = os.path.join(tmp_dir, timestamptoken_file)
                try:
                    with open(timestamptoken_file_path, 'wb') as fout:
                        fout.write(verifyResult.timestamp_token)

                except Exception as err:
                    raise err

                # 取得したタイムスタンプトークンと鍵情報から検証を行う。
                cmd = [
                    api_settings.OPENSSL_MAIN_CMD, api_settings.OPENSSL_OPTION_TS,
                    api_settings.OPENSSL_OPTION_VERIFY, api_settings.OPENSSL_OPTION_DATA,
                    file_name, api_settings.OPENSSL_OPTION_IN, timestamptoken_file_path,
                    api_settings.OPENSSL_OPTION_CAFILE,
                    os.path.join(api_settings.KEY_SAVE_PATH, api_settings.VERIFY_ROOT_CERTIFICATE)
                ]
                prc = subprocess.Popen(
                    cmd, shell=False, stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                stdout_data, stderr_data = prc.communicate()
                ret = api_settings.TIME_STAMP_TOKEN_UNCHECKED

                if stdout_data.__str__().find(api_settings.OPENSSL_VERIFY_RESULT_OK) > -1:
                    ret = api_settings.TIME_STAMP_TOKEN_CHECK_SUCCESS
                    verify_result_title = api_settings.TIME_STAMP_TOKEN_CHECK_SUCCESS_MSG  # 'OK'

                else:
                    ret = api_settings.TIME_STAMP_TOKEN_CHECK_NG
                    verify_result_title = api_settings.TIME_STAMP_TOKEN_CHECK_NG_MSG  # 'NG'

                verifyResult.inspection_result_status = ret
                verifyResult.validation_user = userid
                verifyResult.validation_date = timezone.now()

            if not verifyResult.update_user:
                verifyResult.update_user = None
                verifyResult.update_date = None
                operator_user = OSFUser.objects.get(id=verifyResult.create_user).fullname
                operator_date = verifyResult.create_date.strftime('%Y/%m/%d %H:%M:%S')

            else:
                operator_user = OSFUser.objects.get(id=verifyResult.update_user).fullname
                operator_date = verifyResult.update_date.strftime('%Y/%m/%d %H:%M:%S')

            verifyResult.save()
        except Exception as err:
            logging.exception(err)

        # RDMINFO: TimeStampVerify
        if provider == 'osfstorage':
            if not baseFileNode._path:
                filename = self.get_filenameStruct(baseFileNode, '')
            else:
                filename = baseFileNode._path
            filepath = baseFileNode.provider + filename
            abstractNode = self.get_abstractNode(baseFileNode.node_id)
        else:
            filepath = provider + path
            abstractNode = self.get_abstractNode(Guid.objects.get(_id=project_id).object_id)

        ## RDM Logger ##
        rdmlogger = RdmLogger(rdmlog, {})
        rdmlogger.info(
            'RDM Project', RDMINFO='TimeStampVerify', result_status=ret, user=guid,
            project=abstractNode.title, file_path=filepath, file_id=file_id)

        return {
            'verify_result': ret,
            'verify_result_title': verify_result_title,
            'operator_user': operator_user,
            'operator_date': operator_date,
            'filepath': filepath
        }

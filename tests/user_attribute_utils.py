# -*- coding: utf-8 -*-
import json


class MockResponse:
    def __init__(self, json_data, status_code):
        self.text = None if json_data is None else json.dumps(json_data)
        self.status_code = status_code


mock_data = {
    'userAttribute': {
        'en': {
            'startDate': '',
            'endDate': '',
            'suffix': '',
            'rangeType': [],
            'eRadId': '',
            'organizationType': None,
            'familyNameKana': '',
            'researchMapId': '',
            'middleName': '',
            'aliasKana': '',
            'middleNameKana': '',
            'givenNameKana': '',
            'familyName': '',
            'fullName': 'Tanaka Taro',
            'positionId': None,
            'organizationId': None,
            'fullNameKana': '',
            'idp': None,
            'alias': '',
            'range': [],
            'suffixKana': '',
            'givenName': ''
        },
        'ja': {
            'startDate': '',
            'endDate': '',
            'suffix': 'サフィックス',
            'rangeType': [],
            'eRadId': '',
            'organizationType': None,
            'familyNameKana': '田中',
            'researchMapId': '',
            'middleName': '',
            'aliasKana': '',
            'middleNameKana': '',
            'givenNameKana': 'タロウ',
            'familyName': '田中',
            'fullName': '田中　太郎',
            'positionId': None,
            'organizationId': None,
            'fullNameKana': 'タナカ　タロウ',
            'idp': None,
            'alias': 'エイリアス',
            'range': [],
            'suffixKana': 'safix',
            'givenName': '太郎'
        }
    }
}

mock_response = {
    'userAttribute': MockResponse(
        {
            'meta': {
                'version': '2.6'
            },
            'data': mock_data['userAttribute']
        },
        200
    )
}

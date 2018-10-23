# coding:utf-8
import json


class MockResponse:
    def __init__(self, json_data, status_code):
        self.text = None if json_data is None else json.dumps(json_data)
        self.status_code = status_code


mock_data = {
    'project': {
        'en': {
            'status': '1',
            'startDate': '2018-08-27',
            'endDate': '2018-08-31',
            'description': 'Explanation',
            'rangeType': [ '分野分類１' ],
            'title': 'Mock Project Title',
            'organizationUnit': '管理部署１',
            'researchField': '領域１',
            'range': [ '分野１' ],
            'projectIdentification': 'プロジェクト識別１'
        },
        'ja': {
            'status': '1',
            'startDate': '2018-08-27',
            'endDate': '2018-08-31',
            'description': '研究の説明',
            'rangeType': [ '分野分類１' ],
            'title': 'ハロー',
            'organizationUnit': '管理部署１',
            'researchField': '領域１',
            'range': [ '分野１' ],
            'projectIdentification': 'プロジェクト識別１'
        }
    },
    'funding': {
        'en': {
            'fundings': [
                {
                    'status': 'StatusB',
                    'startDate': '2017-08-01',
                    'endDate': '2018-10-01',
                    'awardTitle': 'Money Tree',
                    'funderSubjectReachDegree': 'Sample Subject Reach Degree',
                    'availableFunds': 'Available FundsB',
                    'totalIndirectCosts': 70000,
                    'budgetCategory': 'Budget CategoryB',
                    'fundingProgramme': 'Sample Funding Programee',
                    'payments': [
                        {
                            'indirectCosts': '20000',
                            'paymentYear': '2018',
                            'directCosts': '50000'
                        }
                    ],
                    'funderId': 'Funder IdentifierB',
                    'funderReference': 'Richard Rich',
                    'totalDirectCosts': 250000,
                    'applicants': [
                        {
                            'name': 'John',
                            'alternativeName': 'Jonny'
                        }
                    ]
                }
            ]
        },
        'ja': {
            'fundings': [
                {
                    'status': 'StatusA',
                    'startDate': '2017-08-01',
                    'endDate': '2018-10-01',
                    'awardTitle': 'じゃんけんに勝つ確率を上がる新たな方法',
                    'funderSubjectReachDegree': 'Sample Subject Reach Degree',
                    'availableFunds': 'Available FundsA',
                    'totalIndirectCosts': 2500000,
                    'budgetCategory': 'Budget CategoryA',
                    'fundingProgramme': 'さくら高校',
                    'payments': [
                        {
                            'indirectCosts': '500000',
                            'paymentYear': '2017',
                            'directCosts': '1000000'
                        }
                    ],
                    'funderId': 'Funder IdentifierA',
                    'funderReference': 'じゃんけんv2',
                    'totalDirectCosts': 4000000,
                    'applicants': [{ 'name': '一郎二郎' }]
                }
            ]
        }
    },
    'contributor': {
        'en': {
            'contributors': [
                {
                    'userName': 'admin',
                    'researchOrganizationId': '科研機関１',
                    'contributorRemarks': 'Sample Contributor Remarks',
                    'name': 'John Contributor',
                    'permission': True,
                    'alternatives': [{ 'value': 'Alternative1' }],
                    'idpId': 'IdP識別１',
                    'representationSetting': 'コントリビュータログ表示設定１',
                    'organizationType': '所属機関分類１',
                    'storageDepOrganizationId': 'ストレージ管理部門機関識別１',
                    'visible': False,
                    'version': True,
                    'contributorType': 'コントリビュータタイプ１',
                    'assignSituation': 'Edited field',
                    'organizationRecognitionId': '機関組織識別１',
                    'id': 'jqxfn'
                }
            ]
        }
    }
}

mock_response = {
    'project': MockResponse(
        {
            'meta': {
                'version': '2.6'
            },
            'data': mock_data['project']
        },
        200
    ),
    'funding': MockResponse(
        {
            'meta': {
                'version': '2.6'
            },
            'data': mock_data['funding']
        },
        200
    ),
    'contributor': MockResponse(
        {
            'meta': {
                'version': '2.6'
            },
            'data': mock_data['contributor']
        },
        200
    )
}

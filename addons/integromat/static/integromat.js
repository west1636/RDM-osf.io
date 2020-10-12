'use strict';

var $ = require('jquery');

var moment = require('moment');

$(function () {
    $('#startScenario').on('click', function () {
        alert('test')
        const payload = {
        'data': [
          {
            'guid': 'xxx',
            'startDate': 'yyy',
            'duration': 'zzz',
            'description': 'aaa'
          }
        ]
      }
    });
});

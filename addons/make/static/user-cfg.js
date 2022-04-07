'use strict';

var MakeUserConfig = require('./makeUserConfig.js').MakeUserConfig;
var url = '/api/v1/settings/make/accounts/';
new MakeUserConfig('#makeScope', url);

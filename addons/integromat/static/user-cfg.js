'use strict';

var IntegromatUserConfig = require('./IntegromatUserConfig.js').IntegromatUserConfig;
var url = '/api/v1/settings/Integromat/accounts/';
new IntegromatUserConfig('#IntegromatAddonScope', url);

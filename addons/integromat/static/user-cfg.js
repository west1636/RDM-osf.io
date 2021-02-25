'use strict';

var IntegromatUserConfig = require('./integromatUserConfig.js').IntegromatUserConfig;
var url = '/api/v1/settings/Integromat/accounts/';
new IntegromatUserConfig('#IntegromatAddonScope', url);

'use strict';

var integromatNodeConfig = require('./integromatNodeConfig.js').integromatNodeConfig;

var url = window.contextVars.node.urls.api + 'settings/integromat/';

new integromatNodeConfig('Integromat', '#integromatScope', url, '#integromatGrid');

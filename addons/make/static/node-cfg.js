'use strict';

var MakeNodeConfig = require('./makeNodeConfig.js').MakeNodeConfig;
var url = window.contextVars.node.urls.api + 'make/settings/';
new MakeNodeConfig('Make', '#makeScope', url, '#makeGrid');

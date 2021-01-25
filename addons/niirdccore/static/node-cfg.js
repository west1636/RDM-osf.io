'use strict';

var $ = require('jquery');
var osfHelpers = require('js/osfHelpers');
var SHORT_NAME = 'niirdccore';

function NodeSettings() {
  var self = this;
}

var settings = new NodeSettings();
osfHelpers.applyBindings(settings, `#${SHORT_NAME}Scope`);

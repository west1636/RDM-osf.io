var $osf = require('js/osfHelpers');
var IntegromatUserViewModel = require('./integromatUserConfig.js').IntegromatUserViewModel;

// Endpoint for Integromat user settings
var url = '/api/v1/settings/integromat/';

var IntegromatUserViewModel = new IntegromatUserViewModel(url);
$osf.applyBindings(IntegromatUserViewModel, '#integromatAddonScope');

// Load initial Integromat data
IntegromatUserViewModel.fetch(url);

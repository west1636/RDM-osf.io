var $osf = require('js/osfHelpers');
var IntegromatViewModel = require('./integromatUserConfig.js').IntegromatViewModel;

// Endpoint for Integromat user settings
var url = '/api/v1/settings/integromat/';

var integromatViewModel = new IntegromatViewModel(url);
$osf.applyBindings(integromatViewModel, '#integromatAddonScope');

// Load initial Integromat data
integromatViewModel.fetch(url);

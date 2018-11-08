var $ = require('jquery');
var ko = require('knockout');
var osfHelpers = require('js/osfHelpers');
var WidgetPane = require('js/widgetpane');

var WidgetPaneModel = function(options) {

  var self = this;

  self.togglePane = options.togglePane;

};

var init = function(commentPaneSelector) {
  var widgetPane = new WidgetPane(commentPaneSelector, {});
  var viewModel = new WidgetPaneModel({togglePane: widgetPane.toggle});

  osfHelpers.applyBindings(viewModel, commentPaneSelector);

  return viewModel;
};

module.exports = {
  init: init,
};

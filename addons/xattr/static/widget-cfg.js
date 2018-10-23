var XattrWidget = require('./js/xattrWidget.js');

var url = window.contextVars.node.urls.api + 'xattr/widget/contents/';
// #xattrScope will only be in the DOM if the addon is properly configured
if ($('#xattrScope')[0]) {
    new XattrWidget('#xattrScope', url);
}

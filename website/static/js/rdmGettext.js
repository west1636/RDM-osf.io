/*globals self: false */
'use strict';

var langSetting = ['en','ja'];
var defaultLanguage = 'en';
var osfLanguageProfileBaseName = 'osfLanguage';

var getBrowserLang = function() {
    var language = defaultLanguage;
    var browserLanguage = (window.navigator.languages && window.navigator.languages[0]) ||
                window.navigator.language ||
                window.navigator.userLanguage ||
                window.navigator.browserLanguage;

    for(var i=0 ; i<langSetting.length ; i++){
        if(browserLanguage === langSetting[i]){
            language = browserLanguage;
        }
    }
    return language;
};

var rdmGettext = function() {
    var language = getBrowserLang();
    var langTranslations = require('js/translations/' + language + '.json' );
    var Gettext = require('node-gettext');
    var gt = new Gettext();
                        
    gt.addTranslations(language, 'messages', langTranslations);
    gt.setLocale(language);
    return gt;
};

var OsfLanguage = function() {
    var browserlanguage = getBrowserLang();
    var osfLanguage = require('js/translations/' + osfLanguageProfileBaseName + '_' + browserlanguage);
    self.language = osfLanguage;
    if(arguments.length > 0) {
        for(let i = 0; i < arguments.length; i++) {
            self.language = self.language[arguments[i]];
        }
    }
    self.t = function(msgid) {
        var msgstr = self.language[msgid];
        if(arguments.length > 1) {
            for(let i = 1; i < arguments.length; i++) {
                msgstr = msgstr[arguments[i]];
            }
        }
        return msgstr;
    };
};

module.exports = {
    rdmGettext: rdmGettext,
    getBrowserLang: getBrowserLang,
    OsfLanguage: OsfLanguage
};


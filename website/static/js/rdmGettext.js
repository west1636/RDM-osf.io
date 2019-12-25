/*globals self: false */
'use strict';

var acceptLanguages = ['en','ja'];
var defaultLanguage = 'en';
var osfLanguageProfileBaseName = 'osfLanguage';

var getBrowserLang = function() {
    var language = defaultLanguage;
    var browserLanguage = (window.navigator.languages && window.navigator.languages[0]) ||
                window.navigator.language ||
                window.navigator.userLanguage ||
                window.navigator.browserLanguage;

    for(var i=0 ; i<acceptLanguages.length ; i++){
        if(browserLanguage === acceptLanguages[i]){
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
    var defaultDomain = [].slice.call(arguments);
    this.languages = {};
    for(var i = 0; i < acceptLanguages.length; i++) {
        var language = require('js/translations/' + osfLanguageProfileBaseName + '_' + acceptLanguages[i]);
        for(var j = 0; j < defaultDomain.length; j++) {
            language = language[defaultDomain[j]];
        }
        self.languages[acceptLanguages[i]] = language;
    }

    this.t = function(msgid) {
        var msgid = [].slice.call(arguments);
        var browserlanguage = getBrowserLang();
        var msgstr = self.languages[browserlanguage];
        for(var i = 0; i < msgid.length; i++) {
            msgstr = msgstr[msgid[i]];
        }
        return msgstr;
    };
};

module.exports = {
    rdmGettext: rdmGettext,
    getBrowserLang: getBrowserLang,
    OsfLanguage: OsfLanguage
};


'use strict';

var langSetting = ['en','ja'];
var defaultLanguage = 'en';
var osfLanguageProfileBasicName = 'osfLanguage'

var getBrowserLang = function() {

    var language = (window.navigator.languages && window.navigator.languages[0]) ||
                window.navigator.language ||
                window.navigator.userLanguage ||
                window.navigator.browserLanguage;
                
    var languageFlag = false;
    for(var i=0 ; i<langSetting.length ; i++){
        
        if(language == langSetting[i]){
         
            languageFlag = true;
        }
    }
         
    if(languageFlag == false){
        
      language = defaultLanguage;  
    }   
 
    return language;
};

var rdmGettext = function() {

    var language = getBrowserLang();

    var langTranslations = require('js/translations/' + language + '.json' );
    var Gettext = require('node-gettext');
    var gt = new Gettext();
                        
    gt.addTranslations(language, 'messages', langTranslations)
    gt.setLocale(language)
 
    return gt;
};

var getOsfLanguage = function(dKey , cKey) {

        var language = getBrowserLang();
        var osfLanguage = require('js/' + osfLanguageProfileBasicName + '_' + language);
 
        var path = [dKey, cKey]
        var index = 0;
        length = path.length;

        while (osfLanguage != null && index < length) {
            osfLanguage = osfLanguage[path[index++]];
        }
        var languageObj =  (index && index == length) ? osfLanguage : undefined; 
        
        return languageObj
}

var t = function(cKey) {

    var tStr = getOsfLanguage(cKey)
 
    return tStr;
};

module.exports = {
    rdmGettext:rdmGettext,
    getOsfLanguage: getOsfLanguage,
    getBrowserLang: getBrowserLang,
    t: t,
};

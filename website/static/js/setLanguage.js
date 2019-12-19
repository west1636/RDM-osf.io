'use strict';

var langSetting = ['en','ja'];
var defaultLanguage = 'en';

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

var setLanguage = function() {

    var language = getBrowserLang();

    var langTranslations = require('js/translations/' + language + '.json' );
    var Gettext = require('node-gettext');
    var gt = new Gettext();
                        
    gt.addTranslations(language, 'messages', langTranslations)
    gt.setLocale(language)
 
    return gt;
};

var getOsfLanguage = function(key,cKey,language) {

        var osfLanguage = require('js/osfLanguage');
 
        var path = [key, cKey, language]
        var index = 0;
        length = path.length;

        while (osfLanguage != null && index < length) {
        osfLanguage = osfLanguage[path[index++]];
        }
        var languageObj =  (index && index == length) ? osfLanguage : undefined; 
        //var languageStr = JSON.stringify( languageObj )
        return languageObj
}

module.exports = {
    setLanguage:setLanguage,
    getOsfLanguage: getOsfLanguage,
    getBrowserLang: getBrowserLang
};




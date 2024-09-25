'use strict';
var hljs = require('highlight.js');
require('highlight-css');
var MarkdownIt = require('markdown-it');

var escapeHtml = require('escape-html');
var $ = require('jquery');
var $osf = require('js/osfHelpers');
var insDel = require('markdown-it-ins-del');
var pymarkdownList = require('js/markdown-it-pymarkdown-lists');

var highlighter = function (str, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(lang, str).value;
            } catch (__) {}
        }

        try {
            return hljs.highlightAuto(str).value;
        } catch (__) {}

        return ''; // use external default escaping
    };

    function underline(md) {
        function underlineRule(state, silent) {
            const startMarker = '\\<u>';
            const endMarker = '\\</u>';
            var pos = state.pos;
            if (state.src.slice(pos, pos + startMarker.length) !== startMarker) {
                return false;
            }
    
            const endPos = state.src.indexOf(endMarker, pos);
            if (endPos === -1) return false;  
            if (!silent) {  
                state.push('underline_open', 'underline', state.level++);
                const textContent = state.src.slice(pos + startMarker.length, endPos);
                const innerTokens = md.parse(textContent, state.env);
                var color = '';
                innerTokens[1].children.forEach(function(token) {
                    state.push(token.type, token.tag, token.nesting, token.level, token.attrs);
                    if (token.type === 'colortext_open') {  
                        color = token.info
                    }
                    if (token.type === 'code_inline') {  
                        state.tokens[state.tokens.length - 1].attrs = [['style', 'color: ' + color + ';']];
                    }
                    if (token.content){
                        state.tokens[state.tokens.length - 1].content = token.content;
                    }
                    if (token.info){
                        state.tokens[state.tokens.length - 1].info = token.info;
                    }
                });
                state.push('underline_close', 'underline', --state.level);
            }
            state.pos = endPos + endMarker.length;
            return true;
        }
    
        md.inline.ruler.after('text', 'underline', underlineRule);
        md.renderer.rules.underline_open = function() { return '<u>'; };
        md.renderer.rules.underline_close = function() { return '</u>'; };
    }

    function colortext(md) {
        function colortextRule(state, silent) {
            const startMarker = '\\<span style="color:';
            const regex = /\\<span style="color:\s*([^>]+)">/;
            const endMarker = '\\</span>';
            var pos = state.pos;
            if (state.src.slice(pos, pos + startMarker.length) !== startMarker) {
                return false;
            }
  
            const endPos = state.src.indexOf(endMarker, pos);
            if (endPos === -1) return false;  
            if (!silent) { 
                const match = regex.exec(state.src.slice(pos));
                const color = match[1];
                state.push('colortext_open', 'colortext', state.level++);
                state.tokens[state.tokens.length - 1].info = color;
                const textContent = state.src.slice(pos + match[0].length, endPos);
                const innerTokens = md.parse(textContent, state.env);
                innerTokens[1].children.forEach(token => {
                    state.push(token.type, token.tag, token.nesting, token.level, token.attrs);
                    if (token.type === 'code_inline') {   
                        state.tokens[state.tokens.length - 1].attrs = [['style', 'color: ' + color + ';']];
                    }
                    if (token.content){
                        state.tokens[state.tokens.length - 1].content = token.content;
                    }
                });
                state.push('colortext_close', 'colortext', --state.level);
            }
            state.pos = endPos + endMarker.length;
            return true;
        }
    
        md.inline.ruler.after('text', 'colortext', colortextRule);
        md.renderer.rules.colortext_open = function(tokens, idx) {
            const color = tokens[idx].info;
            return '<span style="color: ' + color + '">';
        };
        md.renderer.rules.colortext_close = function() { return '</span>'; };
    }

var inlineCodeColor = function(md) {
    md.renderer.rules.code_inline = (tokens, idx) => {
        const token = tokens[idx];
        const style = token.attrs ? token.attrs.find(attr => attr[0] === 'style')[1] : '';
        return '<code style="' + style + '">' + md.utils.escapeHtml(token.content) + '</code>';
    };
}

/**
 * Apply .table class (from Bootstrap) to all tables
 */
var bootstrapTable = function(md) {
    md.renderer.rules.table_open = function() { return '<table class="table">'; };
};

var oldMarkdownList = function(md) {
    md.block.ruler.after('hr', 'pyMarkdownList', pymarkdownList);
};

var WATERBUTLER_REGEX = new RegExp(window.contextVars.waterbutlerURL + 'v1\/resources\/[a-zA-Z0-9]{1,}\/providers\/[a-z0-9]{1,}\/');

var viewOnlyImage = function(md) {
    var defaultRenderer = md.renderer.rules.image;
    md.renderer.rules.image = function (tokens, idx, options, env, self) {
        var token = tokens[idx];
        var imageLink = token.attrs[token.attrIndex('src')][1];
        if (imageLink.match(WATERBUTLER_REGEX) && $osf.urlParams().view_only) {
            token = tokens[idx];
            imageLink = token.attrs[token.attrIndex('src')][1];
            token.attrs[token.attrIndex('src')][1] = imageLink + '&view_only=' + $osf.urlParams().view_only;
            tokens[idx] = token;
        }
        return defaultRenderer(tokens, idx, options, env, self);
    };
};

var mfrURL = window.contextVars.node.urls.mfr;
var osfURL = window.contextVars.osfURL;

var getMfrUrl = function (guid) {
    var mfrLink = mfrURL + 'render?url='+ osfURL + guid + '/download/?action=download%26mode=render';
    if ($osf.urlParams().view_only) {
        mfrLink += '%26view_only=' + $osf.urlParams().view_only;
    }
    return mfrLink;
};

var mfrId = 0;

// Full markdown renderer for views / wiki pages / pauses between typing
var markdown = new MarkdownIt('commonmark', {
    highlight: highlighter,
    linkify: true
    }).use(require('@centerforopenscience/markdown-it-atrules'), {
        type: 'osf',
        pattern: /^http(?:s?):\/\/(?:www\.)?[a-zA-Z0-9 .:]{1,}\/render\?url=http(?:s?):\/\/[a-zA-Z0-9 .:]{1,}\/([a-zA-Z0-9]{1,})\/\?action=download|(^[a-zA-Z0-9]{1,}$)/,
        format: function(assetID) {
             var id = '__markdown-it-atrules-' + mfrId++;
             return '<div id="' + id + '" class="mfr mfr-file"></div>' +
                 '<script>$(document).ready(function () {new mfr.Render("' + id + '", "' + getMfrUrl(assetID) + '");    }); </script>';
        }
    })
    .use(require('@centerforopenscience/markdown-it-video'))
    .use(require('@centerforopenscience/markdown-it-toc'))
    .use(require('markdown-it-sanitizer'))
    .use(viewOnlyImage)
    .use(require('@centerforopenscience/markdown-it-imsize'))
    .use(insDel)
    .enable('table')
    .enable('linkify')
    .use(bootstrapTable)
    .use(inlineCodeColor)
    .use(colortext)
    .use(underline)
    .disable('strikethrough');


// Fast markdown renderer for active editing to prevent slow loading/rendering tasks
var markdownQuick = new MarkdownIt('commonmark', { linkify: true })
    .use(require('markdown-it-sanitizer'))
    .use(viewOnlyImage)
    .use(require('@centerforopenscience/markdown-it-imsize'))
    .disable('link')
    .disable('image')
    .use(insDel)
    .enable('table')
    .enable('linkify')
    .use(bootstrapTable)
    .disable('strikethrough');

// Markdown renderer for older wikis rendered before switch date
var markdownOld = new MarkdownIt('commonmark', { linkify: true})
    .use(require('markdown-it-sanitizer'))
    .use(require('@centerforopenscience/markdown-it-imsize'))
    .use(insDel)
    .enable('table')
    .enable('linkify')
    .use(bootstrapTable)
    .use(oldMarkdownList)
    .disable('strikethrough');

module.exports = {
    full: markdown,
    quick: markdownQuick,
    old: markdownOld
};

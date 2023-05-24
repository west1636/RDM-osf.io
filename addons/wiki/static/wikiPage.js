'use strict';
var ko = require('knockout');
var $ = require('jquery');
var $osf = require('js/osfHelpers');
//var mathrender = require('js/mathrender');
var md = require('js/markdown').full;
var mdQuick = require('js/markdown').quick;
var mdOld = require('js/markdown').old;
var diffTool = require('js/diffTool');
var $osf = require('js/osfHelpers');
var _ = require('js/rdmGettext')._;

var THROTTLE = 500;

var yProseMirror = require('y-prosemirror');

var mCore = require('@milkdown/core');
var mCommonmark = require('@milkdown/preset-commonmark');
var mNord = require('@milkdown/theme-nord');
var mHistory = require('@milkdown/plugin-history');
var mEmoji = require('@milkdown/plugin-emoji');
var mUpload = require('@milkdown/plugin-upload');
var mMath = require('@milkdown/plugin-math');
var mClipboard = require('@milkdown/plugin-clipboard');
var mSlash = require('@milkdown/plugin-slash');
var mGfm = require('@milkdown/preset-gfm');
require('@milkdown/theme-nord/style.css');
require('@milkdown/prose/view/style/prosemirror.css');
require('@milkdown/prose/tables/style/tables.css');
var mBlock = require('@milkdown/plugin-block');
var mCursor = require('@milkdown/plugin-cursor');
var mListener = require('@milkdown/plugin-listener');
var mPrism = require('@milkdown/plugin-prism');
//var mDiagram = require('@milkdown/plugin-diagram');
var mIndent = require('@milkdown/plugin-indent');
var mTooltip = require('@milkdown/plugin-tooltip');
var mUtils = require('@milkdown/utils');
var mCollab = require('@milkdown/plugin-collab');
var yWebsocket = require('y-websocket');
var yjs = require('yjs');
//var yLeveldb =  require('y-leveldb');
var currentOutput = '';
var mEdit;

var readonly = true;
const editable = () => !readonly;

/*
console.log(mCore);
console.log(mCommonmark);
console.log(mUtils);
console.log(mNord);
console.log(mHistory);
console.log(mEmoji);
console.log(mUpload);
console.log(mMath);
console.log(mClipboard);
console.log(mSlash);
console.log(mGfm);
console.log(mBlock);
console.log(mCursor);
console.log(mListener);
console.log(mPrism);
console.log(mTooltip);
//console.log(mDiagram);
console.log(mIndent);
console.log(mCollab);
*/

async function createMEditor(editor, viewVM, temp) {
    console.log('----createMEditor 1------');
    console.log(temp)
    if (editor && editor.destroy) {
        console.log('123');
        editor.destroy();
        console.log('456');
    }
    var mEdit = await mCore.Editor
      .make()
      .config(ctx => {
        ctx.set(mCore.rootCtx, '#mEditor')
        ctx.get(mListener.listenerCtx).markdownUpdated((ctx, markdown, prevMarkdown) => {
//        ctx.get(mListener.listenerCtx).updated((ctx, markdown, prevMarkdown) => {
            console.log(prevMarkdown);
            console.log(markdown);
            viewVM.displaySource(markdown);
        })
        ctx.update(mCore.editorViewOptionsCtx, (prev) => ({
            ...prev,
            editable,
        }))
//        ctx.set(mCore.defaultValueCtx, m)
      })
      .config(mNord.nord)
      .use(mCommonmark.commonmark)
      .use(mHistory.history)
      .use(mEmoji.emoji)
      .use(mUpload.upload)
      .use(mMath.math)
      .use(mClipboard.clipboard)
      .use(mGfm.gfm)
      .use(mBlock.block)
      .use(mCursor.cursor)
      .use(mListener.listener)
      .use(mPrism.prism)
    //  .use(mTooltip.tooltipFactory)
    //  .use(mDiagram.diagram)
        .use(mIndent.indent)
      .use(mCollab.collab)
    //  .use(mSlash.slashFactory)
      .create()
    console.log(mEdit);

    const doc = new yjs.Doc();
    const docId = window.contextVars.wiki.metadata.docId;
    const wsProvider = new yWebsocket.WebsocketProvider('ws://localhost:1234', docId, doc);

    mEdit.action((ctx) => {
        const collabService = ctx.get(mCollab.collabServiceCtx);
        wsProvider.on('sync', isSynced => {
          console.log('sync')
          console.log(isSynced)
        })
        wsProvider.on('status', event => {
          console.log(event.status) // logs "connected" or "disconnected"
        })
        wsProvider.on('connection-close', WSClosedEvent => {
          console.log(WSClosedEvent) // logs "connected" or "disconnected"
        })
        wsProvider.on('connection-error', WSClosedEvent => {
          console.log(WSClosedEvent) // logs "connected" or "disconnected"
        })
        console.log(wsProvider);
        const fullname = window.contextVars.currentUser.fullname;
        console.log(window.contextVars.wiki.metadata.docId);
        console.log(doc);

        wsProvider.awareness.setLocalStateField('user', { name: fullname, color: '#ffb61e'})
        collabService.bindDoc(doc).setAwareness(wsProvider.awareness)

        wsProvider.once('synced', async (isSynced) => {
            if (isSynced) {
                collabService
                .applyTemplate(temp)
                .connect();
            }
        });
        console.log(mEdit.action(mUtils.getMarkdown()))
        console.log('--createMEditor end----')
    })
    return mEdit;

}
//<div id="preview" data-bind="mathjaxify">
ko.bindingHandlers.mathjaxify = {
    update: function(element, valueAccessor, allBindingsAccessor, data, context) {
        var vm = context.$data;
        //Need to unwrap the data in order for KO to know it's changed.
        ko.unwrap(valueAccessor());

        if(vm.allowMathjaxification() && vm.allowFullRender()) {
//            mathrender.mathjaxify('#' + element.id);
        }
    }
};


function ViewWidget(visible, version, viewText, rendered, contentURL, allowMathjaxification, allowFullRender, editor) {
    var self = this;
    self.version = version;
    self.viewText = viewText; // comes from EditWidget.viewText
    self.rendered = rendered;
    self.visible = visible;
    self.allowMathjaxification = allowMathjaxification;
    self.editor = editor;
    self.allowFullRender = allowFullRender;
    self.renderTimeout = null;
    self.displaySource = ko.observable('');
    self.debouncedAllowFullRender = $osf.debounce(function() {
        self.allowFullRender(true);
    }, THROTTLE);

    self.renderMarkdown = function(rawContent){
        if(self.visible()) {
            if (self.allowFullRender()) {
                return md.render(rawContent);
            } else {
                return mdQuick.render(rawContent);
            }
        } else {
            return '';
        }
    };

    if (typeof self.editor !== 'undefined') {
        self.editor.on('change', function () {
            if(self.version() === 'preview') {
                // Quick render
                self.allowFullRender(false);

                // Full render
                self.debouncedAllowFullRender();
            }
        });
    } else {
        self.allowFullRender(true);
    }

    self.displayText =  ko.computed(function() {
        self.allowFullRender();
        var requestURL;
        if (typeof self.version() !== 'undefined') {
            if (self.version() === 'preview') {
//                self.rendered(self.renderMarkdown(self.viewText()));
                self.displaySource(self.viewText());
                document.getElementById("mEditor").style.display = "";
                document.getElementById("wikiViewRender").style.display = "none";
            } else {
                document.getElementById("mEditor").style.display = "none";
                document.getElementById("wikiViewRender").style.display = "";
                if (self.version() === 'current') {
                    requestURL = contentURL;
                } else {
                    requestURL= contentURL + self.version();
                }
                var request = $.ajax({
                    url: requestURL
                });

                request.done(function (resp) {
                    if(self.visible()) {
                        var $markdownElement = $('#wikiViewRender');
                        if (resp.wiki_content){
                            var rawContent = resp.wiki_content
                        } else if(window.contextVars.currentUser.canEdit) {
                            var rawContent = _('*Add important information, links, or images here to describe your project.*');
                        } else {
                            var rawContent = _('*No wiki content.*');
                        }
                        if (resp.rendered_before_update) {
                            // Use old md renderer. Don't mathjaxify
                            self.allowMathjaxification(false);
                            self.rendered(mdOld.render(rawContent));
                            $markdownElement.css('display', 'inherit');

                        } else {
                            // Render raw markdown
                            self.allowMathjaxification(true);
                            self.rendered(self.renderMarkdown(rawContent));
                            $markdownElement.css('display', 'inherit');
                        }
                        self.displaySource(rawContent);
                    }
                });
            }
        } else {
            self.displaySource('');
        }
    });
}

    // currentText comes from ViewWidget.displayText
function CompareWidget(visible, compareVersion, currentText, rendered, contentURL) {
    var self = this;

    self.compareVersion = compareVersion;
    self.currentText = currentText;
    self.rendered = rendered;
    self.visible = visible;
    self.contentURL = contentURL;
    self.compareSource = ko.observable('');

    self.compareText = ko.computed(function() {
        var requestURL;
        if (self.compareVersion() === 'current') {
            requestURL = self.contentURL;
        } else {
            requestURL= self.contentURL + self.compareVersion();
        }
        var request = $.ajax({
            url: requestURL
        });
        request.done(function (resp) {
            var rawText = resp.wiki_content;
            self.compareSource(rawText);
        });

    });

    self.compareOutput = ko.computed(function() {
        var output = diffTool.diff(self.compareSource(), self.currentText());
        self.rendered(output);
        return output;
    }).extend({ notify: 'always' });

}


var defaultOptions = {
    editVisible: false,
    viewVisible: true,
    compareVisible: false,
    menuVisible: true,
    canEdit: true,
    viewVersion: 'current',
    compareVersion: 'previous',
    urls: {
        content: '',
        draft: '',
        page: ''
    },
    metadata: {}
};

function ViewModel(options){
    var self = this;
    // enabled?
    self.editVis = ko.observable(options.editVisible);
    self.viewVis = ko.observable(options.viewVisible);
    self.compareVis = ko.observable(options.compareVisible);
    self.menuVis = ko.observable(options.menuVisible);
    // singleVis : checks if the item visible is the only visible column
    self.singleVis = ko.pureComputed(function(){
        var visible = 0;
        var single;
        if(self.editVis()){
            visible++;
            single = 'edit';
        }
        if(self.viewVis()){
            visible++;
            single = 'view';
        }
        if(self.compareVis()){
            visible++;
            single = 'compare';
        }
        if(visible === 1){
            return single;
        }
        return false;
    });

    self.pageTitle = $(document).find('title').text();

    self.compareVersion = ko.observable(options.compareVersion);
    self.viewVersion = ko.observable(options.viewVersion);
    self.draftURL = options.urls.draft;
    self.contentURL = options.urls.content;
    self.pageURL = options.urls.page;
    self.editorMetadata = options.metadata;
    self.canEdit = options.canEdit;

    self.viewText = ko.observable('');
    self.renderedView = ko.observable('');
    self.renderedCompare = ko.observable('');
    self.allowMathjaxification = ko.observable(true);
    self.allowFullRender = ko.observable(true);
    self.viewVersionDisplay = ko.computed(function() {
        var versionString = '';
        if (self.viewVersion() === 'preview') {
            versionString = _('Live preview');
        } else if (self.viewVersion() === 'current'){
            versionString = _('Current version');
        } else if (self.viewVersion() === 'previous'){
            versionString = _('Previous version');
        } else {
            versionString = _('Version ') + self.viewVersion();
        }
        return versionString;
    });
    // Save initial query params (except for the "mode" query params, which are handled
    // by self.currentURL), so that we can preserve them when we mutate window.history.state
    var initialParams = $osf.urlParams();
    delete initialParams.view;
    delete initialParams.edit;
    delete initialParams.compare;
    delete initialParams.menu;
    self.initialQueryParams = $.param(initialParams);

    self.currentURL = ko.computed(function() {
        // Do not change URL for incompatible browsers
        if (typeof window.history.replaceState === 'undefined') {
            return;
        }

        var paramPrefix = '?';
        var url = self.pageURL;
        // Preserve initial query params
        if (self.initialQueryParams) {
            url += paramPrefix + self.initialQueryParams;
            paramPrefix = '&';
        }
        // Default view is special cased
        if (!self.editVis() && self.viewVis() && self.viewVersion() === 'current' && !self.compareVis() && self.menuVis()) {
            window.history.replaceState({}, '', url);
            return;
        }

        if (self.editVis()) {
            url += paramPrefix + 'edit';
            paramPrefix = '&';
        }
        if (self.viewVis()) {
            url += paramPrefix + 'view';
            paramPrefix = '&';
            if  ((!self.editVis() && self.viewVersion() !== 'current' ) ||
                 (self.editVis() && self.viewVersion() !== 'preview')) {
                url += '=' + self.viewVersion();
            }
        }
        if (self.compareVis()) {
            url += paramPrefix + 'compare';
            paramPrefix = '&';
            if (self.compareVersion() !== 'previous'){
                url += '=' + self.compareVersion();
            }
        }
        if (self.menuVis()) {
            url += paramPrefix + 'menu';
        }

        window.history.replaceState({}, self.pageTitle, url);
    });


    if(self.canEdit) {
        self.editor = ace.edit('editor'); // jshint ignore: line

        var ShareJSDoc = require('addons/wiki/static/ShareJSDoc.js');
        self.editVM = new ShareJSDoc(self.draftURL, self.editorMetadata, self.viewText, self.editor);
    }
    self.viewVM = new ViewWidget(self.viewVis, self.viewVersion, self.viewText, self.renderedView, self.contentURL, self.allowMathjaxification, self.allowFullRender, self.editor);
    self.compareVM = new CompareWidget(self.compareVis, self.compareVersion, self.viewVM.displaySource, self.renderedCompare, self.contentURL);
    var request = $.ajax({
        url: self.contentURL
    });
    request.done(function (resp) {
        if (resp.wiki_content){
            var rawContent = resp.wiki_content
        } else if(window.contextVars.currentUser.canEdit) {
            var rawContent = _('*Add important information, links, or images here to describe your project.*');
        } else {
            var rawContent = _('*No wiki content.*');
        }
        mEdit = createMEditor(mEdit, self.viewVM, rawContent);
    });
    var bodyElement = $('body');
    bodyElement.on('togglePanel', function (event, panel, display) {
        // Update self.editVis, self.viewVis, or self.compareVis in viewmodel
        self[panel + 'Vis'](display);
        //URL needs to be a computed observable, and this should just update the panel states, which will feed URL
        // Switch view to correct version
        if (panel === 'edit') {
            if (display) {
                self.viewVersion('preview');
            } else if (self.viewVersion() === 'preview') {
                self.viewVersion('current');
            }
        } else if (panel === 'view') {
            if(!display && self.compareVis() && self.editVis()){
                self.viewVersion('preview');
            }
        }
    });

    bodyElement.on('toggleMenu', function(event, menuVisible) {
        self.menuVis(menuVisible);
    });

    self.editMode = function() {
        readonly = false;
        self.viewVersion('preview');
        document.getElementById("mEditorFooter").style.display = "";
    }

    self.editModeOff = function() {
        readonly = true;
        document.getElementById("mEditorFooter").style.display = "none";
    }

    // Submit the wysiwyg content as markdown
    self.submitMText = function() {
        console.log(self.viewVM.displaySource());
        var pageUrl = window.contextVars.wiki.urls.page;
        $.ajax({
            url:pageUrl,
            type:'POST',
            data: self.viewVM.displaySource(),
        }).done(function (resp) {
            console.log('success');
            window.location.reload();
        }).fail(function(xhr) {
            var resp = JSON.parse(xhr.responseText);
            var message = resp.message;
            var title = resp.title || 'Problem creating bucket';
            $osf.unblock();
            if (!message) {
                message = 'Looks like that name is taken. Try another name?';
            }
            bootbox.confirm({
                title: $osf.htmlEscape(title),
                message: $osf.htmlEscape(message),
                callback: function(result) {
                    if (result) {
                        self.openCreateBucket();
                    }
                },
                buttons:{
                    confirm:{
                        label:'Try again'
                    }
                }
            });
        });
    }
}



var WikiPage = function(selector, options) {
    var self = this;
    self.options = $.extend({}, defaultOptions, options);

    this.viewModel = new ViewModel(self.options);
    $osf.applyBindings(self.viewModel, selector);
};

module.exports = WikiPage;


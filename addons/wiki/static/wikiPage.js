'use strict';
var ko = require('knockout');
var $ = require('jquery');
var $osf = require('js/osfHelpers');
var mathrender = require('js/mathrender');
var md = require('js/markdown').full;
var mdQuick = require('js/markdown').quick;
var mdOld = require('js/markdown').old;
var diffTool = require('js/diffTool');
var $osf = require('js/osfHelpers');
var _ = require('js/rdmGettext')._;

var THROTTLE = 500;

var yProseMirror = require('y-prosemirror');

var mCore = require('@milkdown/core');
var mTransformer = require('@milkdown/transformer');
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

async function createMEditor(editor, vm, template) {
    console.log('----createMEditor 1------');
    console.log(template)
    if (editor && editor.destroy) {
        console.log('123');
        editor.destroy();
        console.log('456');
    }
    const doc = new yjs.Doc();
    const docId = window.contextVars.wiki.metadata.docId;
    var wsPrefix = (window.location.protocol === 'https:') ? 'wss://' : 'ws://';
    var wsUrl = wsPrefix + window.contextVars.wiki.urls.y_websocket;
    const wsProvider = new yWebsocket.WebsocketProvider(wsUrl, docId, doc);
    var mEdit = await mCore.Editor
      .make()
      .config(ctx => {
        ctx.set(mCore.rootCtx, '#mEditor')
        ctx.get(mListener.listenerCtx).markdownUpdated((ctx, markdown, prevMarkdown) => {
            console.log(prevMarkdown);
            console.log(markdown);
            const collabService = ctx.get(mCollab.collabServiceCtx);
            vm.viewVM.displaySource(markdown);
            collabService
            .applyTemplate('a', (remoteNode, templateNode) => {
                console.log(remoteNode)
                console.log(templateNode)
                console.log('--------listener------------')

//                yjs.applyUpdate(doc, 'a')

//                const pMarkdownSerializer = new pMarkdown.MarkdownSerializer(remoteNode);
//                console.log(pMarkdownSerializer)
//                console.log(pMarkdownSerializer.serialize(remoteNode))
                return false
            })

//            const collabService = ctx.get(mCollab.collabServiceCtx)
//            collabService
//            .applyTemplate(template, (remoteNode, templateNode) => {
//                console.log('---listen---')
//                viewVM.displaySource(remoteNode.textContent);
//                return false
//            })
        })
        ctx.update(mCore.editorViewOptionsCtx, (prev) => ({
            ...prev,
            editable,
        }))
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

    mEdit.action((ctx) => {
        const collabService = ctx.get(mCollab.collabServiceCtx);
        wsProvider.on('sync', isSynced => {
          console.log('sync')
          console.log(isSynced)
        })

        doc.on('update', (update, origin, doc) => {
            console.log(update)
            console.log(origin)
            console.log(doc)
        })

        wsProvider.on('status', event => {
          console.log(event.status) // logs "connected" or "disconnected"
          vm.status(event.status);
          console.log(vm.status)
          if (vm.status !== 'connecting') {
            vm.updateStatus();
          }
          vm.throttledUpdateStatus();
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
//                .applyTemplate(template)
                .applyTemplate(template, (remoteNode, templateNode) => {
                    console.log(remoteNode)
                    console.log(templateNode)
                    if (remoteNode.textContent.length === 0) {
                        vm.viewVM.displaySource(template);
                        return true
                    } else {
//                        const serializer = ctx.get(mCore.serializerCtx)
//                        const remoteDoc = yProseMirror.prosemirrorToYDoc(remoteNode.type)
//                        const markdown = serializer(remoteDoc)
//                        console.log(markdown)
//                          const markdown = mTransformer.Serializer(remoteNode)
//                          console.log(markdown)
//                        viewVM.displaySource('');
                        return false
                    }
                 })
                .connect();
            }
        });
//        const parser = ctx.get(mCore.parserCtx)
//        const node = parser('aaa')
//        const dummyDoc = yProseMirror.prosemirrorToYDoc(node)
//        const dummy = yjs.encodeStateAsUpdate(dummyDoc)
//        yjs.applyUpdate(doc, dummy)
//        console.log(mEdit.action(mUtils.getMarkdown()))
//        mEdit.action(mUtils.insert('1234567890'))
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
            mathrender.mathjaxify('#' + element.id);
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

    self.displayText =  ko.computed(function() {
        self.allowFullRender();
        var requestURL;
        if (typeof self.version() !== 'undefined') {
            if (self.version() === 'preview') {
//                self.rendered(self.renderMarkdown(self.viewText()));
                console.log(self.viewText())
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
    console.log('--CompareWidget--')
    console.log(compareVersion)
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
        console.log(requestURL)
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
    self.viewVis = ko.observable(options.viewVisible);
    self.compareVis = ko.observable(options.compareVisible);
    self.menuVis = ko.observable(options.menuVisible);
    // singleVis : checks if the item visible is the only visible column
    self.singleVis = ko.pureComputed(function(){
        var visible = 0;
        var single;
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

    self.status = ko.observable('connecting');
    self.throttledStatus = ko.observable(self.status());

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

    self.modalTarget = ko.computed(function() {
        switch(self.throttledStatus()) {
            case 'connected':
                return '#connectedModal';
            case 'connecting':
                return '#connectingModal';
            case 'unsupported':
                return '#unsupportedModal';
            default:
                return '#disconnectedModal';
        }
    });

    self.statusDisplay = ko.computed(function() {
        switch(self.throttledStatus()) {
            case 'connected':
                return 'Live editing mode';
            case 'connecting':
                return 'Attempting to connect';
            default:
                return 'Unavailable: Live editing';
        }
    });

    // Throttle the display when updating status.
    self.updateStatus = function() {
        self.throttledStatus(self.status());
    };

    self.throttledUpdateStatus = $osf.throttle(self.updateStatus, 4000, {leading: false});


    self.progressBar = ko.computed(function() {
        switch(self.throttledStatus()) {
            case 'connected':
                return {
                    class: 'progress-bar progress-bar-success',
                    style: 'width: 100%'
                };
            case 'connecting':
                return {
                    class: 'progress-bar progress-bar-warning progress-bar-striped active',
                    style: 'width: 100%'
                };
            default:
                return {
                    class: 'progress-bar progress-bar-danger',
                    style: 'width: 100%'
                };
        }
    });

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
        if (self.viewVis() && self.viewVersion() === 'current' && !self.compareVis() && self.menuVis()) {
            window.history.replaceState({}, '', url);
            return;
        }

        if (self.viewVis()) {
            url += paramPrefix + 'view';
            paramPrefix = '&';
            if  ((self.viewVersion() !== 'current' )) {
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

    self.viewVM = new ViewWidget(self.viewVis, self.viewVersion, self.viewText, self.renderedView, self.contentURL, self.allowMathjaxification, self.allowFullRender, self.editor);
    self.compareVM = new CompareWidget(self.compareVis, self.compareVersion, self.viewVM.displaySource, self.renderedCompare, self.contentURL);

    if(self.canEdit) {
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
            mEdit = createMEditor(mEdit, self, rawContent);
        });
    }
    var bodyElement = $('body');
    bodyElement.on('togglePanel', function (event, panel, display) {
        // Update self.viewVis, or self.compareVis in viewmodel
        self[panel + 'Vis'](display);
        //URL needs to be a computed observable, and this should just update the panel states, which will feed URL
        // Switch view to correct version
        if (panel === 'view') {
            if(!display && self.compareVis()){
                self.viewVersion('preview');
            }
        }
    });

    bodyElement.on('toggleMenu', function(event, menuVisible) {
        self.menuVis(menuVisible);
    });

    // Revert to last saved version, even if draft is more recent
    self.revertChanges = function() {
        console.log('revertChanges');
    };

    self.editMode = function() {
      if(self.canEdit) {
        readonly = false;
        self.viewVersion('preview');
        document.getElementById("editWysiwyg").style.display = "none";
        document.getElementById("mEditorFooter").style.display = "";
      } else{
       // output modal 'can not edit because of your permmission'
      }
    }

    self.editModeOff = function() {
        readonly = true;
        document.getElementById("mEditorFooter").style.display = "none";
        document.getElementById("editWysiwyg").style.display = "";
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
            const reloadUrl = (location.href).replace(location.search, '')
            window.location.assign(reloadUrl);
        }).fail(function(xhr) {
            var resp = JSON.parse(xhr.responseText);
            var message = resp.message;
            console.log(message)
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


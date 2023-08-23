'use strict';
var ko = require('knockout');
var $ = require('jquery');
var $osf = require('js/osfHelpers');
var Raven = require('raven-js');
var Markdown = require('pagedown-ace-converter');
Markdown.getSanitizingConverter = require('pagedown-ace-sanitizer').getSanitizingConverter;
require('imports-loader?Markdown=pagedown-ace-converter!pagedown-ace-editor');

var _ = require('js/rdmGettext')._;

/**
 * Binding handler that instantiates an ACE editor.
 * The value accessor must be a ko.observable.
 * Example: <div data-bind="ace: currentText" id="editor"></div>
 */
var editor;

ko.bindingHandlers.ace = {
    init: function (element, valueAccessor) {
        editor = ace.edit(element.id);  // jshint ignore: line
        editor.renderer.setShowGutter(true);
        editor.renderer.setOption('showLineNumbers', true);
        // Updates the view model based on changes to the editor
        editor.getSession().on('change', function () {
            valueAccessor()(editor.getValue());
        });
    },

    update: function (element, valueAccessor) {
        var content = editor.getValue();        // Content of ace editor
        var value = ko.unwrap(valueAccessor()); // Value from view model
        // Updates the editor based on changes to the view model
        if (value !== undefined && content !== value) {
            var cursorPosition = editor.getCursorPosition();
            editor.setValue(value);
            editor.gotoLine(cursorPosition.row + 1, cursorPosition.column);
        }
    }
};

function ViewModel(url, viewText) {
    var self = this;
    self.initText = ko.observable('');
    self.currentText = viewText; //from wikiPage's VM
    self.activeUsers = ko.observableArray([]);
    self.status = ko.observable('connecting');
    self.throttledStatus = ko.observable(self.status());
    self.autocom = ko.observable(false);

    self.displayCollaborators = ko.computed(function() {
       return (self.activeUsers().length > 1);
    });
    // Display the icons of up to the first 18 collaborators on a page
    self.showCollaborators = ko.computed(function() {
        if (self.activeUsers().length > 18) {
            return self.activeUsers().slice(0,18);
        }
        return self.activeUsers();
    });
    // Show text that says "and # more" collaborators
    self.andOthersMessage = ko.pureComputed(function() {
        if (self.activeUsers().length > 18) {
            var leftovers = self.activeUsers().length - 18;
            return '...and ' + leftovers + ' more';
        }
        return '';
    });
    // Throttle the display when updating status.
    self.updateStatus = function() {
        self.throttledStatus(self.status());
    };

    self.throttledUpdateStatus = $osf.throttle(self.updateStatus, 4000, {leading: false});

    self.status.subscribe(function (newValue) {
        if (newValue !== 'connecting') {
            self.updateStatus();
        }
        self.throttledUpdateStatus();
    });

    self.statusDisplay = ko.computed(function() {
        switch(self.throttledStatus()) {
            case 'connected':
                return _('Live editing mode');
            case 'connecting':
                return _('Attempting to connect');
            case 'unsupported':
                return _('Unsupported browser');
            default:
                return _('Unavailable: Live editing');
        }
    });

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

    self.wikisDiffer = function(wiki1, wiki2) {
        // Handle inconsistencies in newline notation
        var clean1 = typeof wiki1 === 'string' ?
            wiki1.replace(/(\r\n|\n|\r)/gm, '\n') : '';
        var clean2 = typeof wiki2 === 'string' ?
            wiki2.replace(/(\r\n|\n|\r)/gm, '\n') : '';
        return clean1 !== clean2;
    };

    self.changed = function() {
        return self.wikisDiffer(self.initText(), self.currentText());
    };
    // Fetch initial wiki text
    self.fetchData = function() {
        var request = $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json'
        });
        request.done(function (response) {
            // Most recent version, whether saved or in mongo
            self.initText(response.wiki_draft);
        });
        request.fail(function (xhr, textStatus, error) {
            $osf.growl('Error',_('The wiki content could not be loaded.'));
            self.status('disconnected');
            Raven.captureMessage(_('Could not GET wiki contents.'), {
                extra: {
                    url: url,
                    textStatus: textStatus,
                    error: error
                }
            });
        });
        return request;
    };
    // Revert to last saved version, even if draft is more recent
    self.revertChanges = function() {
        return self.fetchData().then(function(response) {
            // Dirty check now covers last saved version
            self.initText(response.wiki_content);
            self.currentText(response.wiki_content);
        });
    };

    $(window).on('beforeunload', function() {
        if (self.changed() && self.status() !== 'connected') {
            return _('There are unsaved changes to your wiki. If you exit ') +
                _('the page now, those changes may be lost.');
        }
    });

    $(document).ready(function() {
        $('#autocom').on('change', function() {
            self.autocom($(this).is(':checked'));
        });
    });

}

function WikiEditor(url, viewText, editor) {
    this.viewModel = new ViewModel(url, viewText);
    var mdConverter = Markdown.getSanitizingConverter();
    var mdEditor = new Markdown.Editor(mdConverter);
    mdEditor.run(editor);

}

module.exports = WikiEditor;

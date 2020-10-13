'use strict';

var $ = require('jquery');
var moment = require('moment');
var osfHelpers = require('js/osfHelpers');

$(function () {
    $('#startScenario').on('click', function () {
        alert('test')

        var self = this;
        self.guid = ko.observable();
        self.zoomTopic = ko.observable();
        self.zoomStartDate = ko.observable();
        self.zoomDuration = ko.observable();
        self.zoomDescription = ko.observable();
        var url ='/api/v1/project/' + self.guid + '/integromat/register_conference'

        // Selection should not be empty
        if (!self.zoomTopic() ){
            self.changeMessage('Please enter a topic.', 'text-danger');
            return;
        }
        if (!self.zoomStartDate() ){
            self.changeMessage('Please enter a start date.', 'text-danger');
            return;
        }
        if (!self.zoomStartTime() ){
            self.changeMessage('Please enter a start time', 'text-danger');
            return;
        }
        return osfHelpers.postJSON(
            url,
            ko.toJS({
                guid: self.guid(),
                zoom_topic: self.zoomTopic(),
                zoom_start_date: self.zoomStartDate(),
                zoom_start_time: self.zoomStartTime(),
                zoom_duration: self.zoomDuration(),
                zoom_description: self.zoomDescription(),
        })
        ).done(function() {
            self.clearModal();
            $modal.modal('hide');
            $('#integromatRegisterConferenceModal').modal('hide');

        }).fail(function(xhr, textStatus, error) {
            var errorMessage = (xhr.status === 401) ? '401' : 'Invalid integromat server';
            self.changeMessage(errorMessage, 'text-danger');
            Raven.captureMessage('Could not authenticate with Integromat', {
                url: self.url,
                textStatus: textStatus,
                error: error
            });
        });
    });
});

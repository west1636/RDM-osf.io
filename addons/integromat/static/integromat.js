'use strict';

var $ = require('jquery');
var ko = require('knockout');
var moment = require('moment');
var osfHelpers = require('js/osfHelpers');

$(function () {
    $('#startScenario').on('click', function () {

        var self = this;

        var teamsGuid = $("#teams_guid").val();
        var teamsSubject = $("#teams_subject").val();
        var teamsStartDate = $("#teams_start_date").val();
        var teamsStartTime = $("#teams_start_time").val();
        var teamsEndDate = $("#teams_end_date").val();
        var teamsEndTime = $("#teams_end_time").val();
        var teamsAttendees = $("#teams_attendees").val();
        var teamsLocation = $("#teams_location").val();
        var teamsContent = $("#teams_content").val();

        var url ='/api/v1/project/' + teamsGuid + '/integromat/register_conference'
/*
        // Selection should not be empty
        if (!self.teamsTopic() ){
            self.changeMessage('Please enter a topic.', 'text-danger');
            return;
        }
        if (!self.teamsStartDate() ){
            self.changeMessage('Please enter a start date.', 'text-danger');
            return;
        }
        if (!self.teamsStartTime() ){
            self.changeMessage('Please enter a start time', 'text-danger');
            return;
        }
*/
        return osfHelpers.postJSON(
            url,
            ko.toJS({
                guid: teamsGuid,
                teams_subject: teamsSubject,
                teams_attendees: teamsAttendees,
                teams_start_date: teamsStartDate,
                teams_start_time: teamsStartTime,
                teams_end_date: teamsEndDate,
                teams_end_time: teamsEndTime,
                teams_location: teamsLocation,
                teams_content: teamsContent,
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

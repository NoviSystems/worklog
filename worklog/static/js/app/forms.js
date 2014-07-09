"use strict";

/* global WorkItem */
/* global JobSelectField */
/* global HoursInputField */
/* global RepoSelectField */
/* global IssueSelectField */
/* global TextTextareaField */
/* global DeleteFormButton */
/* global SaveEditButton */
/* global worklog */
/* global repos */
/* global formTable */
/* global displayTable */
/* global workItemFormSet */


function Form(properties) {

    if (properties) {
        this.fields = properties.fields;
        this.selector = properties.selector;        
    }

    this.submit = function() {
        throw "NotImplementedError";
    };
}

function WorkItemForm(workItem, selector, formset) {

    this.selector = '#' + selector;

    this.job = new JobSelectField(workItem.job.id, this.selector);
    this.hours = new HoursInputField(workItem.hours, this.selector);
    this.repo = new RepoSelectField(workItem.repo.github_id, this.selector);
    this.issue = new IssueSelectField(workItem.issue.github_id, this.selector);
    this.text = new TextTextareaField(workItem.text, this.selector);
    this.removeFormButton = new DeleteFormButton(this.selector);
    this.saveFormButton = new SaveFormButton(this.selector);

    this.formset = formset;

    this.workItem = workItem;

    this.flatWorkItem = workItem.flatten();

    var fields = {
        job: this.job,
        hours: this.hours,
        repo: this.repo,
        issue: this.issue,
        text: this.text,
        removeFormButton: this.removeFormButton,
        saveFormButton: this.saveFormButton
    };

    this.context = {
        id: this.selector.substring(1, this.selector.length),
        job: {
            class: 'col-md-2',
            value: this.job.html()
        },
        hours: {
            class: 'col-md-2',
            value: this.hours.html()
        },
        repo: {
            class: 'col-md-2',
            value: this.repo.html()
        },
        issue: {
            class: 'col-md-2',
            value: this.issue.html()
        },
        text: {
            class: 'col-md-3',
            value: this.text.html()
        },
        buttons: [
            {
                value: this.saveFormButton.html()
            },
            {
                value: this.removeFormButton.html()
            }
        ]
    };

    Form.call(this, {"fields": fields, "selector": this.selector});

    this.populateIssues = function(repo) {
        $(this.selector + ' .issue').empty();
        $(this.selector + ' .issue').append('<option value="None" selected="selected">None</option>');
        if (repo) {

            var issues = repos[repo].issues;

            issues.sort(function (a, b) {
                if (a.number < b.number) {
                    return -1;
                }
                if (a.number > b.number) {
                    return 1;
                }
                return 0;
            });

            for (var i in issues) {
                $(this.selector + ' .issue').append('<option value="' + issues[i].github_id + '">' + issues[i].number + ': ' + issues[i].title + '</option>');
            }
            if (this.issue.value) {

                var value = this.issue.value;
                var valueInList = $.grep(issues, function(issue) {
                    return issue.github_id === value;
                });

                if (valueInList.length > 0) {
                    $(this.selector + ' .issue').val(this.issue.value);                    
                } else {
                    $(this.selector + ' .issue').val('None');
                    this.issue.value = null;
                }
            }
        }
    };

    this.post = function() {

        var selector = this.selector;
        var form = this;

        $.ajax({
            type: 'POST',
            url: '/worklog/api/workitems/',
            cache: false,
            data: this.flatWorkItem,
            success: function(data) {
                formTable.removeForm(selector, 'slow', $(window).width() < 600);
                formTable.addWorkItem(new WorkItem($.parseJSON(data)));

                $('#reconcile').attr('disabled', 'disabled');

                var reconcile = {
                    user: worklog.userid,
                    date: worklog.date,
                    reconciled: true
                };

                $.ajax({
                    type: 'POST',
                    url: '/worklog/api/workdays/',
                    cache: false,
                    data: reconcile,
                    dataType: 'text' 
                });
            },
            error: function (data){
                var response = $.parseJSON(data.responseText);
                for (var key in response) {
                    form.appendErrorMessageToField(response[key], key);
                    $(selector).addClass('danger');
                    $(selector).on('click', function() {
                        $(this).removeClass('danger');
                    });
                }
            },
            dataType: 'text' 
        });
    };

    this.put = function() {

        var selector = this.selector;
        var form = this;

        $.ajax({
            type: 'PUT',
            url: '/worklog/api/workitems/' + workItem.id + '/',
            cache: false,
            data: this.flatWorkItem,
            success: function(data, status) {

                if ($(this.selector).hasClass('danger')) {
                    $(this.selector).removeClass('danger');
                }

                formTable.restoreRow(new WorkItem($.parseJSON(data)));

                if ($(window).width() < 600) {
                    $('.bs-edit-modal-sm .modal-body').children().remove();
                    $('.bs-edit-modal-sm').modal('toggle');
                }

                $(selector).addClass('success', function() {
                    $(selector).addClass('workitem-fade', function() {
                        $(selector).removeClass('success', function() {
                            window.setTimeout(function () {
                                $(selector).removeClass('workitem-fade');
                            }, 2000);
                        });
                    });
                });                                        
            },
            error: function(data) {
                var response = $.parseJSON(data.responseText);
                var row = formTable.rowsBySelector[selector];

                if (!row) {
                    row = workItemFormSet.getForm(selector);
                }

                for (var key in response) {
                    row.appendErrorMessageToField(response[key], key);
                    $(selector).addClass('danger', function() {
                        $(selector).addClass('workitem-fade', function() {
                            $(selector).removeClass('danger', function() {
                                window.setTimeout(function() {
                                    $(selector).removeClass('workitem-fade');
                                }, 2000);
                            });
                        });
                    });
                }  
            },
            dataType: 'text'
        });
    };

    this.appendErrorMessageToField = function(message, field) {
        var erroneousField = this.selector + ' .' + field;
        $(this.selector).addClass('has-error');


        if ($(erroneousField).siblings().length !== 0) {
            $(erroneousField).siblings('label').text(message);
        } else {
            $(erroneousField).after('<label class="control-label" for="' + erroneousField + '" id="label-' + this.selector[13] + '">' + message + '</label>');
        }
    };
}

WorkItemForm.prototype = new Form();
WorkItemForm.prototype.constructor = WorkItemForm;
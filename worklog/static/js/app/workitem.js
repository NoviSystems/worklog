"use strict";

var jobList = [];
var repoList = [];
var issueList = [];

var jobs = {};
var repos = {};
var issues = {};
var workItems = {};

var formTable = null;
var displayTable = null;

var workItemFormSet = new FormSet();

function API () {}

API.getJobs = function() {
    return $.getJSON('/worklog/api/jobs/?date=' + worklog.date + '&user=' + worklog.userid, null, function(data, status) {
        jobList = data;
        jobList.sort(function(a, b) {
            if (a.name < b.name) { return -1; }
            if (a.name > b.name) { return 1; }
            return 0;
        });

        for (var i = 0; i < jobList.length; i++) {
            var key = jobList[i].id;
            jobs[key.toString()] = jobList[i];
        }
    });  
};

API.getRepos = function() { 
    return $.getJSON('/worklog/api/repos/', null, function(data, status) {
        repoList = data;
        repoList.sort(function(a, b) {
            if (a.name < b.name)
                return -1;
            if (a.name > b.name)
                return 1;
            return 0;
        });
        for (var i = 0; i < repoList.length; i++) {
            var key = repoList[i].github_id;
            repos[key.toString()] = repoList[i];
        }
    });
};

API.getIssues = function() {
    return $.getJSON('/worklog/api/issues/', null, function(data, status) {
        issueList = data;
        for (var i = 0; i < issueList.length; i++) {
            var key = issueList[i].github_id;
            issues[key.toString()] = issueList[i];
        }

        for (var i = 0; i < repoList.length; i++) {
            repoList[i].issues = [];
            for (var j = 0; j < issueList.length; j++) {
                if (repoList[i].github_id == issueList[j].repo) {
                    repoList[i].issues.push(issueList[j]);
                }
            }
        }
    });
};

API.assignIssuesToRepos = function() {
    for (var i = 0; i < repoList.length; i++) {
        repoList[i].issues = [];
        for (var j = 0; j < issueList.length; j++) {
            if (repoList[i].github_id == issueList[j].repo) {
                repoList[i].issues.push(issueList[j]);
            }
        }
    }  
};

API.getWorkDay = function() {
    return $.getJSON('/worklog/api/workdays/?date=' + worklog.date +'&user=' + worklog.userid, null, function(data) {
        if (data[0]) {
            if (data[0].reconciled) {
                $('#reconcile').attr('disabled', 'disabled');
            }            
        }
    });
};

function WorkItem(workItemJSON) {

    this.id = null;
    this.user = null;
    this.date = null;
    this.job = {
        id: null,
        name: null,
    };
    this.hours = null;
    this.repo = {
        github_id: null,
        name: null
    };
    this.issue = {
        github_id: null,
        title: null,
        number: null
    };
    this.text = null;

    if (workItemJSON) {
        this.id = workItemJSON.id;
        this.user = workItemJSON.user;
        this.date = workItemJSON.date;
        this.job.id = workItemJSON.job
        if (jobs[workItemJSON.job.toString()])
            this.job.name = jobs[workItemJSON.job.toString()].name;
        this.hours = workItemJSON.hours;
        if (workItemJSON.repo) {
            this.repo.github_id = workItemJSON.repo;
            this.repo.name = repos[workItemJSON.repo.toString()].name;             
        }
        if (workItemJSON.issue) { 
            this.issue.github_id = workItemJSON.issue;
            this.issue.title = issues[workItemJSON.issue.toString()].title;
            this.issue.number = issues[workItemJSON.issue.toString()].number;
        }
        this.text = workItemJSON.text;

        workItems[this.id] = this;
    }

    this.flatten = function() {
        return {
            id: this.id,
            user: this.user,
            date: this.date,
            job: this.job.id,
            hours: this.hours,
            repo: this.repo.github_id,
            issue: this.issue.github_id,
            text: this.text
        }
    }
}

function Session(csrftoken) {
    var csrftoken = csrftoken;

    this.getCSRFToken = function() {
        return csrftoken;
    }

    this.setupAJAX = function() {
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        function sameOrigin(url) {
            // test that a given url is a same-origin URL
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });         
    }
}


$(document).ready(function() {

    $("[data-toggle=tooltip]").tooltip();


    var currentSession = new Session($.cookie('csrftoken'));
    currentSession.setupAJAX();

    var promise = $.when(API.getJobs(), API.getRepos(), API.getIssues(), API.getWorkDay());

    promise.done(function() {

        API.assignIssuesToRepos();

        var rowSource = $('#row-template').html();
        var rowTemplate = Handlebars.compile(rowSource);

        var formRowSource = $('#modal-form-template').html();
        var formRowTemplate = Handlebars.compile(formRowSource);

        displayTable = new WorkItemDisplayTable(rowTemplate);        
        formTable = new WorkItemFormTable(rowTemplate);
        

        $('.table tbody').on('change', '.repo', function() {
            var form = $(this).data('row');
            var repo = $(this).val();
            workItemFormSet.forms[form].populateIssues(repo);
        });

        $('#form-table tbody').on('click', '.delete', function() {
            var selector = $(this).data('row');
            formTable.removeForm(selector, 'fast');
        });

        $('#submit').on('click', function() {
            workItemFormSet.post();
        });

        $('#add-form').on('click', function() {
            formTable.addForm();
        });

        $('textarea.form-control.imput-sm.text').keydown(function(e) {
            console.log(e.keyCode);
            if (e.keyCode == 13) {
                e.preventDefault();
            }
        });

        $('tbody').keydown(function(e) {
            console.log(e.keyCode);
        });

        $('#display-table tbody').on('click', '.edit', function() {
            if ($(window).width() < 600) {
                var workItem = $(this).data('workitem');
                var newForm = new WorkItemForm(workItems[workItem], 'modal-' + workItem, null);
                workItemFormSet.addForm(newForm);
                var context = {
                    tableID: 'form-table',
                    smallWindow: $(window).width() < 600,
                    row: {
                        id: 'modal-' + workItem,
                        job: newForm.job.toHtml(),
                        hours: newForm.hours.toHtml(),
                        repo: newForm.repo.toHtml(),
                        issue: newForm.issue.toHtml(),
                        text: newForm.text.toHtml()
                    }
                };
                $(formRowTemplate(context)).appendTo('.bs-edit-modal-sm .modal-body');
                $('.bs-edit-modal-sm #save').attr('data-workitem', $(this).data('workitem'));

                $('.bs-edit-modal-sm .table').on('change', '.repo', function() {
                    var form = $(this).data('row');
                    var repo = $(this).val();
                    workItemFormSet.forms[form].populateIssues(repo);
                });

                newForm.populateJobs();
                newForm.populateRepos();
            } else {
                displayTable.editRow($(this).data('workitem'));            
            }
        });

        $('#display-table tbody').on('click', '.delete', function() {
            $('.modal #delete').attr('data-workitem', $(this).data('workitem'));
        });

        $('.bs-delete-modal-sm').on('click', '#delete', function() {
            displayTable.deleteWorkItem($(this).attr('data-workitem'));
            $('.bs-delete-modal-sm').modal('toggle');
        });

        $('.bs-edit-modal-sm').on('click', '#save', function() {
            var id = $(this).attr('data-workitem');
            workItemFormSet.saveWorkItem('#modal-' + id);
        });

        $('.bs-edit-modal-sm').on('click', '#cancel', function() {
            $('.bs-edit-modal-sm .modal-body').children().remove();
        });

        $('.bs-edit-modal-sm').on('click', '.close', function() {
            $('.bs-edit-modal-sm .modal-body').children().remove();  
        });

        $('#display-table tbody').on('click', ' .save', function() {
            workItemFormSet.saveWorkItem('#' + $(this).data('workitem'));
        });

        $('#display-table tbody').on('click', ' .cancel', function() {
            displayTable.restoreRow(workItems[$(this).data('workitem')]);
        });

        $('.alert').alert();

        $('#reconcile').on('click', function() {

            $(this).attr('disabled', 'disabled');

            var data = {
                user: worklog.userid,
                date: worklog.date,
                reconciled: true
            };

            $.ajax({
                type: 'POST',
                url: '/worklog/api/workdays/',
                cache: false,
                data: data,
                dataType: 'text' 
            });
        });
    });
});

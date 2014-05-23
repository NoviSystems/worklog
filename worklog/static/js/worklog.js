var jobList = [];
var repoList = [];
var issueList = [];

var jobs = {};
var repos = {};
var issues = {};



var getJobs = function() {
    return $.getJSON(worklog.url + '/worklog/api/jobs/?available_all_users=True&date=' + worklog.date, null, function(data, status) {
        jobList = data;
        jobList.sort(function(a, b) {
            if (a.name < b.name)
                return -1;
            if (a.name > b.name)
                return 1;
            return 0;
        });

        for (var i = 0; i < jobList.length; i++) {
            var key = jobList[i].id;
            jobs[key.toString()] = jobList[i];
        }
    });    
}


var getRepos = function() { 
    return $.getJSON(worklog.url + '/worklog/api/repos/', null, function(data, status) {
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
}

var getIssues = function(repo) {
    return $.getJSON(worklog.url + '/worklog/api/issues/', null, function(data, status) {
        issueList = data;
        for (var i = 0; i < issueList.length; i++) {
            var key = issueList[i].github_id;
            issues[key.toString()] = issueList[i];
        }
    });
}

$(document).ready(function() {

    var csrftoken = $.cookie('csrftoken');

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

    var formCount = 1;
    var formArray = [0];

    function assignIssuesToRepos() {
        for (var i = 0; i < repoList.length; i++) {
            repoList[i].issues = [];
            for (var j = 0; j < issueList.length; j++) {
                if (repoList[i].github_id == issueList[j].repo) {
                    repoList[i].issues.push(issueList[j]);
                }
            }
        }
    }

    function setIssueSelectWidthInSelector(selector) {
        $(selector + ' #issue').width(160);
    }

    function populateJobsInSelectorWithJobSelected(selector, jobID) {
        for (var i in jobList) {
            $(selector + ' #job').append('<option value="' + jobList[i].id + '">' + jobList[i].name);
        }
        if (jobID) {
            $(selector + ' #job').val(jobID);
        }
    }

    function populateReposInSelectorWithRepoSelected(selector, repoID) {
        for (var i in repoList) {
            $(selector + ' #repo').append('<option value="' + repoList[i].github_id + '">' + repoList[i].name + '</option>');
        }
        if (repoID) {
            $(selector + ' #repo').val(repoID);
            $(selector + ' #repo').change();
        }
    }

    function populateIssuesFromRepoInSelector(repo, selector) {

        $(selector + ' #issue').empty();
        $(selector + ' #issue').append('<option value selected="selected">None</option>');
        if (repo != '') {

            var issues = repos[repo].issues;

            issues.sort(function (a, b) {
                if (a.number < b.number)
                    return -1;
                if (a.number > b.number)
                    return 1;
                return 0;
            });
            for (var i in issues) {
                $(selector + ' #issue').append('<option value="' + issues[i].github_id + '">' + issues[i].number + ': ' + issues[i].title + '</option>');
                setIssueSelectWidthInSelector(selector);
            }
        }
    }

    $('.table tbody').on('change', '#repo', function() {
        populateIssuesFromRepoInSelector($(this).val(), '#' + $(this).parent().parent().parent().attr('id'));
    });

    var $formTemplate =  $('#row-0').clone(true);

    $.when(getJobs(), getRepos(), getIssues()).done(function() {
        populateJobsInSelectorWithJobSelected('#row-0', null);
        populateReposInSelectorWithRepoSelected('#row-0', null);
        assignIssuesToRepos();
    });

    setIssueSelectWidthInSelector('#row-0');

    $('#form-table tbody').on('click', '#delete', function() {
        removeForm('#' + $(this).parent().parent().attr('id'));
    });

    function removeForm(selector) {

        var formNumber = selector[5];
        $(selector).remove();

         for (var j = 0; j < formArray.length; j++) {
            if (formNumber == formArray[j]) {
                formArray.splice(j, 1);
                break;
            }
        }
    }

    $('#submit').on('click', function() {
        for (var i = 0; i < formArray.length; i++) {
            submitWorkItemFromSelector('#row-' + formArray[i], 'POST');
        }
    });

    $('#add-form').on('click', function() {
        addForm();
    });

    function addForm() {

        var $cloned = $formTemplate.clone(true).attr('id', 'row-' + formCount);

        $cloned.appendTo('#form-table');

        populateReposInSelectorWithRepoSelected('#row-' + formCount, null);
        populateJobsInSelectorWithJobSelected('#row-' + formCount, null);
        setIssueSelectWidthInSelector('#row-' + formCount);
        
        formArray = formArray.concat(formCount);
        formCount++;
    };

    function initializeDisplayTable() {
        $.getJSON(worklog.url + "/worklog/api/workitems/?date=" + worklog.date, null, function (data) {
            for (var i = 0; i < data.length; i++) {
                addWorkItemToDisplayTable(data[i]);
            }
        });
    }

    initializeDisplayTable();

    function addWorkItemToDisplayTable(workItem) {

        var jobName = '';
        function getJobName() {
            return $.getJSON(worklog.url + '/worklog/api/jobs/' + workItem.job, null, function(data) {
                jobName = data.name;
            });
        }

        var repoName = '';
        function getRepoName() {
            if (workItem.repo) {
                return $.getJSON(worklog.url + '/worklog/api/repos/' + workItem.repo, null, function(data) {
                    repoName = data.name;
                });                        
            }
        }

        var issueTitle = '';
        function getIssueTitle () {
            if (workItem.issue) {
                return $.getJSON(worklog.url + '/worklog/api/issues/' + workItem.issue, null, function(data) {
                    issueTitle = data.title;
                });
            }
        }

        $.when(getJobName(), getRepoName(), getIssueTitle()).done(function() {
            buildTableRow();
        });

        function buildTableRow() {
            $('#display-table tbody').append(
                '<tr class="workitem" id="' + workItem.id + '">\
                    <td class="col-md-2" id="job" name="' + workItem.job + '">' + jobName + '</td>\
                    <td class="col-md-2" id="hours">' + workItem.hours + '</td>\
                    <td class="col-md-2" id="repo" name="' + (workItem.repo ? workItem.repo : '') + '">' + (repoName ? repoName : 'None') + '</td>\
                    <td class="col-md-2" id="issue" name ="' + (workItem.issue ? workItem.issue : '') + '">' + (issueTitle ? issueTitle : 'None') + '</td>\
                    <td class="col-md-3" id="text">' + workItem.text + '</td>\
                    <td id="controls">\
                        <button type="button" class="btn btn-link btn-xs" id="edit"><span class="glyphicon glyphicon-pencil"></span></button>\
                        <button type="button" class="btn btn-link btn-xs" data-toggle="modal" data-target=".bs-example-modal-sm" id="delete"><span class="glyphicon glyphicon-trash"></span></button>\
                    </td>\
                </tr>'
            );
        }
    }

    $('#display-table tbody').on('click', '#edit', function() {
        makeWorkItemEditable('#' + $(this).parent().parent().attr('id'));
    });

    $('#display-table tbody').on('click', '#delete', function() {
        $('.modal #delete').attr('name', $(this).parent().parent().attr('id'));
    });

    $('.modal').on('click', '#delete', function() {
        submitWorkItemFromSelector('#' + $(this).attr('name'), 'DELETE');
        $('.modal').modal('toggle');
    });

    $('#display-table tbody').on('click', '#save', function() {
        submitWorkItemFromSelector('#' + $(this).parent().parent().attr('id'), 'PATCH');
    });

    $('#display-table tbody').on('click', '#cancel', function() {
        var selector = '#' + $(this).parent().parent().attr('id');
        var wi = buildWorkItemFromSelector(selector, false);
        restoreWorkItem(selector, wi);
    });

    function makeWorkItemEditable(workItem) {

        var $job = $(workItem + ' #job');
        var $hours = $(workItem + ' #hours');
        var $repo = $(workItem + ' #repo');
        var $issue = $(workItem + ' #issue');
        var $text = $(workItem + ' #text');
        var $controls = $(workItem + ' #controls');

        var jobID = $job.attr('name');
        var repoID = $repo.attr('name');
        var issueID = $issue.attr('name');

        function buildForm() {
            $job.replaceWith(
                '<td class="col-md-2">\
                    <div class="form-group">\
                        <select class="form-control input-sm" id="job">\
                            <option value selected="selected">None</option>\
                        </select>\
                    </div>\
                </td>'
            );            

            $hours.replaceWith(
                '<td class="col-md-2">\
                    <div class="form-group">\
                        <input class="form-control input-sm" id="hours" value="' + $hours.text() + '" type="text">\
                    </div>\
                </td>'
            );
            
            $repo.replaceWith(
                '<td class="col-md-2">\
                    <div class="form-group">\
                        <select class="form-control input-sm" id="repo">\
                            <option value selected="selected">None</option>\
                        </select>\
                    </div>\
                </td>'
            );

            $issue.replaceWith(
                '<td class="col-md-2">\
                    <div class="form-group">\
                        <select class="form-control input-sm" id="issue">\
                            <option value selected="selected">None</option>\
                        </select>\
                    </div>\
                </td>'
            );

            $text.replaceWith(
                '<td class="col-md-3">\
                    <div class="form-group">\
                        <textarea class="form-control input-sm" cols="40" id="text" placeholder="Work Description" rows="1">' + $text.text() + '</textarea>\
                    </div>\
                </td>'
            );

            $controls.replaceWith(
                '<td id="controls">\
                    <button type="button" class="btn btn-link btn-xs" id="save"><span class="glyphicon glyphicon-ok"></span></button>\
                    <button type="button" class="btn btn-link btn-xs" id="cancel"><span class="glyphicon glyphicon-remove"></span></button>\
                </td>'
            );  
        }


        buildForm();
        populateJobsInSelectorWithJobSelected(workItem, jobID);
        populateReposInSelectorWithRepoSelected(workItem, repoID);
        setIssueSelectWidthInSelector(workItem);
        $(workItem + ' #issue').val(issueID);
    }

    function restoreWorkItem(selector, workItem) {
        var $job = $(selector + ' #job').parent().parent();
        var $hours = $(selector + ' #hours').parent().parent();
        var $repo = $(selector + ' #repo').parent() .parent();
        var $issue = $(selector + ' #issue').parent().parent();
        var $text = $(selector + ' #text').parent().parent();
        var $edit = $(selector + ' #controls');

        var jobName = '';
        function getJobName() {
            return $.getJSON(worklog.url + '/worklog/api/jobs/' + workItem.job, null, function(data) {
                jobName = data.name;
            });
        }

        var repoName = '';
        function getRepoName() {
            if (workItem.repo) {
                return $.getJSON(worklog.url + '/worklog/api/repos/' + workItem.repo, null, function(data) {
                    repoName = data.name;
                });                        
            }
        }

        var issueTitle = '';
        function getIssueTitle () {
            if (workItem.issue) {
                return $.getJSON(worklog.url + '/worklog/api/issues/' + workItem.issue, null, function(data) {
                    issueTitle = data.title;
                });
            }
        }

        function restoreRow() {
            $job.replaceWith('<td class="col-md-2" id="job" name="' + workItem.job + '">' + jobName + '</td>');
            $hours.replaceWith('<td class="col-md-2" id="hours">' + workItem.hours + '</td>');
            $repo.replaceWith('<td class="col-md-2" id="repo" name="' + (workItem.repo ? workItem.repo : '') + '">' + (repoName ? repoName : 'None') + '</td>');
            $issue.replaceWith('<td class="col-md-2" id="issue" name ="' + (workItem.issue ? workItem.issue : '') + '">' + (issueTitle ? issueTitle : 'None') + '</td>');
            $text.replaceWith('<td class="col-md-3" id="text">' + workItem.text + '</td>');
            $edit.replaceWith(
                '<td id="controls">\
                    <button type="button" class="btn btn-link btn-xs" id="edit"><span class="glyphicon glyphicon-pencil"></span></button>\
                    <button type="button" class="btn btn-link btn-xs" data-toggle="modal" data-target=".bs-example-modal-sm" id="delete"><span class="glyphicon glyphicon-trash"></span></button>\
                </td>'
            );
        }

        $.when(getJobName(), getRepoName(), getIssueTitle()).done(function() {
            restoreRow();
        });
    }

    function appendErrorMessageToField(message, field, selector) {
        var id = selector + ' #' + field;
        $(id).parent().addClass('has-error');

        if ($(id).parent().children('label').length !== 0) {
            $(id).parent().children('label').text(message);
        } else {
            $(id).after('<label class="control-label" for="' + id + '" id="label-' + selector[5] + '">' + message + '</label>');
        }
    }

    function buildWorkItemFromSelector(selector, method) {
        return {
            id: (method !== 'POST' ? selector.substring(1, selector.length) : ""),
            user: worklog.userid,
            date: worklog.date,
            job: $(selector + ' #job').val(),
            hours: $(selector + ' #hours').val(),
            repo: $(selector + ' #repo').val(),
            issue: $(selector + ' #issue').val(),
            text: $(selector + ' #text').val(),
            csrfmiddlewaretoken: worklog.csrfToken,
        }
    }

    function submitWorkItemFromSelector(selector, method) {

        var workItemData = buildWorkItemFromSelector(selector, method);

        $.ajax({
            type: method,
            url: worklog.url + '/worklog/api/workitems/' + (method !== 'POST' ? workItemData.id + '/' : ''),
            data: workItemData,
            success: function(data) {

                if ($(selector).hasClass('danger')) {
                    $(selector).removeClass('danger');
                }

                if (method === 'PATCH') {
                    restoreWorkItem(selector, workItemData);
                    $(selector).addClass('success');
                } else if (method === 'POST') {
                    removeForm(selector); 
                    addWorkItemToDisplayTable(workItemData)
                } else if (method === 'DELETE') {
                    $(selector).remove();
                }
            },
            error: function (data){
                response = $.parseJSON(data.responseText);
                for (var key in response) {
                    appendErrorMessageToField(response[key], key, selector);
                    $(selector).addClass('danger');
                }
            },
            dataType: 'text'
        });
    };

    $('.alert').alert();

    $('.form-control').keydown(function(event) {
        if (event.keyCode == 13) {
            event.preventDefault();
            $('#submit').click();
        }
    });
});
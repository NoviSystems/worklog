$(document).ready(function() {

    var formCount = 1;
    var formArray = [0];

    function setIssueSelectWidth(formNumber) {
        $('#id_form-0-issue').width(160);
    }

    function populateJobs(formNumber) {
        $.getJSON(worklog.url + "/worklog/api/jobs/?available_all_users=True&date=" + worklog.date, null, function(data, status) {
            data.sort(function(a, b) {
                if (a.name < b.name)
                    return -1;
                if (a.name > b.name)
                    return 1;
                return 0;
            });
            for (var i in data) {
                $('#id_form-' + formNumber + '-job').append('<option value="' + data[i].id + '">' + data[i].name);
            }
        });
        return $();
    }

    function populateRepos(formNumber) {
        $.getJSON(worklog.url + "/worklog/api/repos/", null, function(data, status) {
            repos = data
            data.sort(function(a, b) {
                if (a.name < b.name)
                    return -1;
                if (a.name > b.name)
                    return 1;
                return 0;
            });
            for (var i in data) {
                $('#id_form-' + formNumber + '-repo').append('<option value="' + data[i].github_id + '">' + data[i].name + '</option>');
            }
        });
        return $();
    }

    function populateIssues(formNumber, repoID) {
        $('#id_form-' + formNumber + '-issue').empty();
        $('#id_form-' + formNumber + '-issue').append('<option value selected="selected">None</option>');
        if (repoID != '') {

            $.getJSON(worklog.url + "/worklog/api/issues/?repo=" + repoID, null, function(data, status) {
                issues = data
                issues.sort(function (a, b) {
                    if (a.number < b.number)
                        return -1;
                    if (a.number > b.number)
                        return 1;
                    return 0;
                });
                for (var i in issues) {
                    $('#id_form-' + formNumber + '-issue').append('<option value="' + issues[i].github_id + '">' + issues[i].number + ': ' + issues[i].title + '</option>');
                    setIssueSelectWidth(formNumber);
                }
            });
        }
    }

    $('#form-table tbody').on('change', '.form-control', function() {
        if ($(this).attr('id')[10] == 'r') {
            populateIssues($(this).attr('id')[8], $(this).val());
        } 
    });

    var $formTemplate =  $('#row-0').clone(true); 
    populateJobs(0);
    populateRepos(0);
    setIssueSelectWidth(0);

    $('#form-table tbody').on('click', '.btn-danger', function() {
        removeForm($(this).attr('id')[16]);
    });

    function removeForm(formNumber) {
         for (var j = 0; j < formArray.length; j++) {
            if (formNumber == formArray[j]) {
                $('#row-' + formArray[j]).remove();
                formArray.splice(j, 1);
                break;
            }
        }
    }

    $('#submit').on('click', function() {
        for (var i = 0; i < formArray.length; i++) {
            submitWorkItem(formArray[i]);
        }
    });

    $('#add-form').on('click', function() {
        addForm();
    });

    function addForm() {

        var $cloned = $formTemplate.clone(true).attr('id', 'row-' + formCount);

        $cloned.find('#workform-0').attr('id', 'workform-' + formCount);
        $cloned.find('#id_form-0-job').attr('id', 'id_form-' + formCount + '-job');
        $cloned.find('#id_form-0-repo').attr('id', 'id_form-' + formCount + '-repo');
        $cloned.find('#id_form-0-issue').attr('id', 'id_form-' + formCount + '-issue');
        $cloned.find('#id_form-0-hours').attr('id',  'id_form-' + formCount + '-hours');
        $cloned.find('#id_form-0-text').attr('id',  'id_form-' + formCount + '-text')
        $cloned.find('#delete-workform-0').attr('id',  'delete-workform-' + formCount);

        $cloned.appendTo('#form-table');

        populateRepos(formCount);
        populateJobs(formCount);
        setIssueSelectWidth(formCount);
        
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
                '<tr>\
                    <td>'+ worklog.username + '</td>\
                    <td>' + jobName + '</td>\
                    <td>' + workItem.hours + '</td>\
                    <td>' + (repoName ? repoName : 'None') + '</td>\
                    <td>' + (issueTitle ? issueTitle : 'None') + '</td>\
                    <td>' + workItem.text + '</td>\
                </tr>'
            );
        }
    }

    function appendErrorMessageToField(message, field, formNumber) {
        var id = '#id_form-' + formNumber + '-' + field;
        $(id).parent().addClass('has-error');

        if ($(id).parent().children('label').length !== 0) {
            $(id).parent().children('label').text(message);
        } else {
            $(id).after('<label class="control-label" for="' + id + '" id="label-' + formNumber + '">' + message + '</label>');
        }
    }

    function submitWorkItem(formNumber) {
        var postData = {
            user: worklog.userid,
            date: worklog.date,
            job: $('#id_form-' + formNumber + '-job').val(),
            hours: $('#id_form-' + formNumber + '-hours').val(),
            repo: $('#id_form-' + formNumber + '-repo').val(),
            issue: $('#id_form-' + formNumber + '-issue').val(),
            text: $('#id_form-' + formNumber + '-text').val(),
            csrfmiddlewaretoken: worklog.csrfToken,
        }
        $.post(worklog.url + "/worklog/api/workitems/", postData, function(data, status) {
            removeForm(formNumber);
            addWorkItemToDisplayTable(data);
        }).fail(function(data, status) {
            $('#row-' + formNumber).addClass('danger')
            keys = Object.keys(data.responseJSON);
            for (var k in keys) {
                appendErrorMessageToField(data.responseJSON[keys[k]], keys[k], formNumber);
            }
        });
    };

    $('.alert').alert();
});
/* Tables */
function Table() {

}

function WorkItemTable(type) {
    Table.call(this);

    var id = type + '-table';
    this.selector = '#' + id;

    this.rows = [];
    this.rowsBySelector = {};

    this.appendRowToBody = function(row) {
        this.rows.push(row);
        this.rowsBySelector[row.selector] = row;
    };
}
WorkItemTable.prototype = new Table();
WorkItemTable.prototype.constructor = WorkItemTable;


function WorkItemFormTable(rowTemplate) {
    WorkItemTable.call(this, 'form');

    var newForm = new WorkItemForm(new WorkItem(null), 'new-workitem-0', null);

    var context = {
        tableID: 'form-table',
        smallWindow: $(window).width() < 600,
        row: {
            id: 'new-workitem-0',
            job: newForm.job.toHtml(),
            hours: newForm.hours.toHtml(),
            repo: newForm.repo.toHtml(),
            issue: newForm.issue.toHtml(),
            text: newForm.text.toHtml()
        }
    };

    var source = $('#form-table-template').html();
    var template = Handlebars.compile(source);
    var html = template(context);

    $(html).insertBefore('#submit');

    if ($(window).width() < 600) {
        newForm.populateJobs();
        newForm.populateRepos(); 
        workItemFormSet.addForm(newForm);  
    }


    this.addForm = function() {
        var selector = 'new-workitem-' + workItemFormSet.count;
        var newForm = new WorkItemForm(new WorkItem(null), selector, workItemFormSet);
        workItemFormSet.addForm(newForm);

        this.rows.push(newForm);
        this.rowsBySelector['#' + selector] = newForm;

        $(rowTemplate(newForm.context)).appendTo('#form-table tbody').hide().fadeIn('fast');

        newForm.populateJobs();
        newForm.populateRepos();
    };

    if ($(window).width() > 600)
        this.addForm();

    this.removeForm = function(selector, speed, mobile) {
        if (!mobile) {
            workItemFormSet.removeForm(selector);
            $(selector).fadeOut(speed, function() {
                $(selector).remove();
            });            
        } else {
            $('.job').val('');
            $('.hours').val('');
            $('.repo').val('');
            $('.issue').val('');
            $('.text').val('');
        }
    };
}
WorkItemFormTable.prototype = new WorkItemTable();
WorkItemFormTable.prototype.constructor = WorkItemFormTable;


function WorkItemDisplayTable(rowTemplate) {
    WorkItemTable.call(this, 'display');

    var table = this;
    this.rowTemplate = rowTemplate;

    $.when(
        $.getJSON('/worklog/api/workitems/?date=' + worklog.date + '&user=' + worklog.userid, null, function (data) {
            for (var i = 0; i < data.length; i++) {
                var wi = new WorkItem(data[i]);
                table.addWorkItem(wi);
                workItems[wi.id] = wi;
            }
        })
    ).done(function() {
        if ($(window).width() < 600) {
            var $editButtonList = $('#display-table tbody .edit');
            for (var i = 0; i < $editButtonList.length; i++) {
                $($editButtonList[i]).attr('data-toggle', 'modal');
            }            
        }
    });

    this.addWorkItem = function(workItem) {
        
        var context = WorkItemDisplayTable.buildContext(workItem);

        $(this.rowTemplate(context)).appendTo('#display-table tbody').hide().fadeIn('slow');
        if ($(window).width() < 600)
            $('#' + workItem.id + ' .edit').attr('data-toggle', 'modal');
    };

    this.editRow = function(workItem) {

        var selector = workItem;
        workItemObj = workItems[workItem];

        var newForm = new WorkItemForm(workItemObj, selector, workItemFormSet);
        newForm.formset.addForm(newForm);
        this.rowsBySelector[newForm.selector] = newForm;

        newForm.context.text = {
            class: 'col-md-3',
            value: newForm.text.toHtml()
        };
        newForm.context.button = {
            class: 'controls',
            value: (new SaveEditButton(workItem)).toHtml() + (new CancelEditButton(workItem)).toHtml()
        };


        $('#' + selector).replaceWith((this.rowTemplate(newForm.context)));

        newForm.populateJobs();
        newForm.populateRepos();
        if (workItemObj.repo)
            newForm.populateIssues(workItemObj.repo.github_id);
    };

    this.restoreRow = function(workItem) {
        workItems[workItem.id] = workItem;
        var context = WorkItemDisplayTable.buildContext(workItem);
        var boundEdit = $('#display-table #' + workItem.id + ' .edit').clone(true);
        $('#display-table #' + workItem.id).replaceWith(this.rowTemplate(context));
        if ($(window).width() < 600) {
            $('#display-table #' + workItem.id + ' .edit').replaceWith(boundEdit);
        }
    };


    this.deleteWorkItem = function(workItem) {
        var wi = workItems[workItem];
        var selector = '#' + workItem;
        $.ajax({
            type: 'DELETE',
            url: '/worklog/api/workitems/' + workItem + '/',
            data: wi.flatten(),
            success: function(data) {
                $(selector).fadeOut('slow', function() {
                    $(selector).remove();
                });
            },
            error: function (data){
                var response = $.parseJSON(data.responseText);
                for (var key in response) {
                    displayTable.appendErrorMessageToField(response[key], key, selector);
                    $(selector).addClass('danger');
                    $(selector).on('click', function() {
                        $(this).removeClass('danger');
                    });
                }
            },
            dataType: 'text'
        });
    };
}
WorkItemDisplayTable.prototype = new WorkItemTable();
WorkItemDisplayTable.prototype.constructor = WorkItemDisplayTable;

WorkItemDisplayTable.buildContext = function(workItem) {
    return {
        id: workItem.id,
        job: {
            class: 'col-md-2 job',
            value: workItem.job.name,
            name: workItem.job.id
        },
        hours: {
            class: 'col-md-2 hours',
            value: workItem.hours,
        },
        repo: {
            class: 'col-md-2 repo',
            value: (workItem.repo.github_id ? workItem.repo.name : 'None'),
            name: (workItem.repo.github_id ? workItem.repo.github_id : ''),
        },
        issue: {
            class: 'col-md-2 issue',
            value: (workItem.issue.github_id ? workItem.issue.number + ': ' + workItem.issue.title : 'None'),
            name: (workItem.issue.github_id ? workItem.issue.github_id : ''),
        },
        text: {
            class: 'col-md-3 text',
            value: workItem.text
        },
        button: {
            class: 'controls',
            value: (new EditWorkItemButton(workItem.id)).toHtml() + (new DeleteWorkItemButton(workItem.id)).toHtml(),
        }
    };  
};

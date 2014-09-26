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
        headerText: 'New Work Item',
        row: {
            id: 'new-workitem-0',
            job: newForm.job.html(),
            hours: newForm.hours.html(),
            repo: newForm.repo.html(),
            issue: newForm.issue.html(),
            text: newForm.text.html()
        }
    };

    if ($(window).width() < 600) { 
        var html = rowTemplate(context);
        workItemFormSet.addForm(newForm);
        $(html).prependTo('#accordion');
        rivets.bind($(newForm.selector), {
            workitem: newForm.flatWorkItem
        });
    } else {
        var source = $('#form-table-template').html();
        var template = Handlebars.compile(source);
        var html = template(context);
        $(html).insertBefore('#submit');
    }

    this.addForm = function() {
        var selector = 'new-workitem-' + workItemFormSet.count;
        var newForm = new WorkItemForm(new WorkItem(null), selector, workItemFormSet);
        workItemFormSet.addForm(newForm);

        var rows = $('#form-table tbody').children();
        var tail = null;

        $.each(rows, function(index, value) {
            if (value.id[0] !== 'n' && index !== 0) {
                tail = rows[index - 1];
                return false;
            } else if (value.id[0] !== 'n' && index === 0) {
                return false;
            }
        });

        this.rows.push(newForm);
        this.rowsBySelector['#' + selector] = newForm;

        if (tail === null) {
            $(rowTemplate(newForm.context)).prependTo('#form-table tbody').hide().fadeIn('fast');
        } else {
            $(rowTemplate(newForm.context)).insertAfter(tail).hide().fadeIn('fast');            
        }
        rivets.bind($(newForm.selector), {
            workitem: newForm.flatWorkItem
        });
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
            $('.job').val('None');
            $('.hours').val('');
            $('.repo').val('None');
            $('.issue').val('None');
            $('.text').val('');
        }
    };

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
            var $editButtonList = $('#form-table tbody .edit');
            for (var i = 0; i < $editButtonList.length; i++) {
                $($editButtonList[i]).attr('data-toggle', 'modal');
            }            
        }
    });

    this.addWorkItem = function(workItem) {

        if ($(window).width() < 600) {
            var newForm = new WorkItemForm(new WorkItem(null), workItem.id, null);
            newForm.workItem = workItem;
            newForm.flatWorkItem = workItem.flatten();
            workItemFormSet.addForm(newForm);

            context = {
                headerText: workItem.hours + ' hours on ' + workItem.text,
                row: {
                    id: workItem.id,
                    job: newForm.job.html(),
                    hours: newForm.hours.html(),
                    repo: newForm.repo.html(),
                    issue: newForm.issue.html(),
                    text: newForm.text.html()
                }
            };
            $(this.rowTemplate(context)).appendTo('#accordion').hide().fadeIn('slow');
            $(newForm.selector).on('change', '.repo', function() {
                var form = $(this).data('row');
                var repo = $(this).val();
                workItemFormSet.forms[form].populateIssues(repo);
            });
            $('#' + workItem.id + ' .job').val(workItem.job.id);
            $('#' + workItem.id + ' .hours').val(workItem.hours);
            $('#' + workItem.id + ' .repo').val(workItem.repo.github_id);
            $('#' + workItem.id + ' .repo').change();
            $('#' + workItem.id + ' .issue').val(workItem.issue.github_id);
            $('#' + workItem.id + ' .text').val(workItem.text);

            rivets.bind($(newForm.selector), {
                workitem: newForm.flatWorkItem
            });

            $('.panel-heading').on('click', '#save', function(event) {
                event.stopPropagation();
                workItemFormSet.postOrPut($(this).parent().data('target'));
            });
        } else {
            context = WorkItemDisplayTable.buildContext(workItem);
            $(this.rowTemplate(context)).appendTo('#form-table tbody').hide().fadeIn('slow');
        }
    };

    this.editRow = function(workItem) {

        var selector = workItem;
        workItemObj = workItems[workItem];

        var newForm = new WorkItemForm(workItemObj, selector, workItemFormSet);

        newForm.formset.addForm(newForm);
        this.rowsBySelector[newForm.selector] = newForm;

        newForm.context.text = {
            class: 'col-md-3',
            value: newForm.text.html()
        };
        newForm.context.buttons = [
            {
                value: (new SaveEditButton(workItem)).html()
            },
            {
                value: (new CancelEditButton(workItem)).html()
            }
        ];


        $('#' + selector).replaceWith((this.rowTemplate(newForm.context)));
        $('#' + selector + ' .job').val(workItemObj.job.id);

        rivets.bind($('#' + workItem), {
            workitem: newForm.flatWorkItem
        });

        if (workItemObj.repo) {
            $('#' + selector + ' .repo').val(workItemObj.repo.github_id);
            $('#' + selector + ' .repo').change();
        }
    };

    this.restoreRow = function(workItem) {
        workItems[workItem.id] = workItem;
        var context = WorkItemDisplayTable.buildContext(workItem);
        var boundEdit = $('#form-table #' + workItem.id + ' .edit').clone(true);
        $('#form-table #' + workItem.id).replaceWith(this.rowTemplate(context));
        if ($(window).width() < 600) {
            $('#form-table #' + workItem.id + ' .edit').replaceWith(boundEdit);
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
            var $editButtonList = $('#form-table tbody .edit');
            for (var i = 0; i < $editButtonList.length; i++) {
                $($editButtonList[i]).attr('data-toggle', 'modal');
            }            
        }
    });

    this.addWorkItem = function(workItem) {
        
        var context = WorkItemDisplayTable.buildContext(workItem);

        $(this.rowTemplate(context)).appendTo('#form-table tbody').hide().fadeIn('slow');
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

        rivets.bind($('#' + workItem), {
            workitem: newForm.flatWorkItem
        });

    };

    this.restoreRow = function(workItem) {
        workItems[workItem.id] = workItem;
        var context = WorkItemDisplayTable.buildContext(workItem);
        var boundEdit = $('#form-table #' + workItem.id + ' .edit').clone(true);
        $('#form-table #' + workItem.id).replaceWith(this.rowTemplate(context));
        if ($(window).width() < 600) {
            $('#form-table #' + workItem.id + ' .edit').replaceWith(boundEdit);
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
        buttons: [
            {
                value: (new EditWorkItemButton(workItem.id)).html()
            },
            {
                value: (new DeleteWorkItemButton(workItem.id)).html()
            }
        ]
    };         
};

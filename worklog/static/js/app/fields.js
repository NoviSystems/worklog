"use strict";

/* global Handlebars */
/* global jobList */
/* global repoList */

function Field(name, value, context) {
    this.name = name;
    this.value = value;

    var source = $('#' + name + '-field-template').html();
    if (source) {
        var template = Handlebars.compile(source);
        var html = template(context);        
    }

    this.html = function() {
        return html;
    };
}

function SelectField(name, value, data, context) {
    Field.call(this, name, value, context);
}

SelectField.prototype = new Field();
SelectField.prototype.constructor = SelectField;


function JobSelectField(value, data) {

    var options = [{value: '', text: 'None'}];

    for (var i in jobList) {
        options.push({ 
            value: jobList[i].id,
            text: jobList[i].name
        });
    }

    var context = {
        row: {
            id: data
        },
        options: options
    };

    SelectField.call(this, 'job', value, data, context);
}

JobSelectField.prototype = new SelectField();
JobSelectField.prototype.constructor = JobSelectField;


function RepoSelectField(value, data) {

    var options = [{value: '', text: 'None'}];

    for (var i in repoList) {
        options.push({
            value: repoList[i].github_id,
            text: repoList[i].name
        });
    }

    var context = {
        row: {
            id: data
        },
        options: options
    };

    SelectField.call(this, 'repo', value, data, context);
}

RepoSelectField.prototype = new SelectField();
RepoSelectField.prototype.constructor = RepoSelectField;

function IssueSelectField(value, data) {

    var context = {
        row: {
            id: data
        },
        options: [{value: '', text: 'None'}]
    };

    SelectField.call(this, 'issue', value, data, context);
}

IssueSelectField.prototype = new SelectField();
IssueSelectField.prototype.constructor = IssueSelectField;


function InputField(name, value, type, context) {
    Field.call(this, name, value, context);
    this.type = type;
}

InputField.prototype = new Field();
InputField.prototype.constructor = InputField;


function TextareaField(name, value, context) {
    Field.call(this, name, value, context);
}

TextareaField.prototype = new Field();
TextareaField.prototype.constructor = TextareaField;


function ButtonField(button) {
    Field.call(this);

    this.toHtml = function() {
        return button.toHtml();
    };
}

ButtonField.prototype = new Field();
ButtonField.prototype.constructor = ButtonField;


function HoursInputField(value, data) {

    var context = {
        row: {
            id: data
        },
        value: value
    };

    InputField.call(this, 'hours', value, 'text', context);
}

HoursInputField.prototype = new InputField();
HoursInputField.prototype.constructor = HoursInputField;


function TextTextareaField(value, data) {

    var context = {
        row: {
            id: data
        },
        value: value
    };

    TextareaField.call(this, 'text', value, context);
}

TextTextareaField.prototype = new TextareaField();
TextTextareaField.prototype.constructor = TextTextareaField;



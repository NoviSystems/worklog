"use strict";

function Field(name, value) {
    this.name = name;
    this.value = value;

    this.toHtml = function() {
        throw "NotImplementedError";
    }
}


function SelectField(name, value, data) {
    Field.call(this, name, value);
    this.options = [];

    this.addOption = function(value, text) {
        this.options.push(new Option(value, text));
    }

    this.addOptionsFromArray = function(optionsArray) {
        for (var i = 0; i < this.optionsArray.length; i++) {
            this.addOption(optionsArray[i]);
        }
    }

    this.toHtml = function() {

        var htmlString = '<div class="form-group"><select class="form-control input-sm ' + name + '" data-row="' + data +'"><option value="" selected="selected">None</option>'

        for (var i = 0; i < this.options.length; i++) {
            htmlString += options[i].toHtml();
        }

        htmlString += '</select></div>';
        return htmlString;
    }

    function Option(value, text) {
        this.value = value;
        this.text = text;

        this.toHtml = function() {
            return '<option value=' + this.value + '>' + this.text + '</option>';
        }
    }
}

SelectField.prototype = new Field();
SelectField.prototype.constructor = SelectField;


function JobSelectField(value, data) {
    SelectField.call(this, 'job', value, data);
}

JobSelectField.prototype = new SelectField();
JobSelectField.prototype.constructor = JobSelectField;


function RepoSelectField(value, data) {
    SelectField.call(this, 'repo', value, data);
}

RepoSelectField.prototype = new RepoSelectField();
RepoSelectField.prototype.constructor = RepoSelectField;

function IssueSelectField(name, value, data) {
    SelectField.call(this, name, value, data);

    this.addOption = function(value, text, number) {
        this.options.push(new Option(value, text, number));
    }

    function Option(value, text, number) {
        this.value = value;
        this.text = text;
        this.number = number;

        this.toHtml = function() {
            return '<option value=' + this.value + '>' + this.number + ': ' + this.text + '</option>';
        }
    }
}

IssueSelectField.prototype = new SelectField();
IssueSelectField.prototype.constructor = IssueSelectField;


function InputField(name, value, type) {
    Field.call(this, name, value);
    this.type = type;
}

InputField.prototype = new Field();
InputField.prototype.constructor = InputField;


function TextareaField(name, value) {
    Field.call(this, name, value);
}

TextareaField.prototype = new Field();
TextareaField.prototype.constructor = TextareaField;


function ButtonField(button) {
    Field.call(this);

    this.toHtml = function() {
        return button.toHtml();
    }
}

ButtonField.prototype = new Field();
ButtonField.prototype.constructor = ButtonField;


function WorkItemInputField(name, value, type, data) {
    InputField.call(this, name, value, type);

    this.toHtml = function() {
        return '<div class="form-group">\
                    <input class="form-control input-sm ' + name + '" placeholder="Hours Worked" type="' + type + '" data-row="' + data + '" value="' + (value ? value : '') + '">\
                </div>';
    }
}

WorkItemInputField.prototype = new InputField();
WorkItemInputField.prototype.constructor = WorkItemInputField;


function WorkItemTextareaField(name, value, data) {
    TextareaField.call(this, name, value);
    
    this.toHtml = function() {
        return '<div class="form-group">\
                    <textarea class="form-control input-sm ' + name + '" cols="40" placeholder="Work Description" rows="1" data-row="' + data + '">' + (value ? value : '') + '</textarea>\
                </div>';
    }
}

WorkItemTextareaField.prototype = new TextareaField();
WorkItemTextareaField.prototype.constructor = WorkItemTextareaField;



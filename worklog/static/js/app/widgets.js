function Button() {

}

function AddFormButton() {
    Button.call(this);

    this.toHtml = function() {
        return '<button class="btn btn-primary btn-xs" type="button" id="add-form">+</button>';
    }
}

function DeleteFormButton(row) {
    Button.call(this);

    this.toHtml = function() {
        return '<button class="btn btn-danger btn-xs delete" type="button" data-row="' + row + '">&times;</button>';
    }
}

function DeleteWorkItemButton(workItem) {
    Button.call(this);

    this.toHtml = function() {
        return '<button type="button" class="btn btn-link btn-xs delete" data-toggle="modal" data-target=".bs-delete-modal-sm" data-workitem="' + workItem + '"><span class="glyphicon glyphicon-trash"></span></button>'
    }
}

DeleteWorkItemButton.prototype = new Button();
DeleteWorkItemButton.prototype.constructor = DeleteWorkItemButton;


function EditWorkItemButton(workItem) {
    Button.call(this);

    this.toHtml = function() {
        return '<button type="button" class="btn btn-link btn-xs edit" data-target=".bs-edit-modal-sm" data-workitem="' + workItem + '"><span class="glyphicon glyphicon-pencil"></span></button>'
    }
}

EditWorkItemButton.prototype = new Button();
EditWorkItemButton.prototype.constructor = EditWorkItemButton;


function SaveEditButton(workItem) {
    Button.call(this);

    this.toHtml = function() {
        return '<button type="button" class="btn btn-link btn-xs save" data-workitem="' + workItem + '"><span class="glyphicon glyphicon-ok"></span></button>'
    }
}

SaveEditButton.prototype = new Button();
SaveEditButton.prototype.constructor = SaveEditButton;


function CancelEditButton(workItem) {
    Button.call(this);

    this.toHtml = function() {
        return '<button type="button" class="btn btn-link btn-xs cancel" data-workitem="' + workItem + '"><span class="glyphicon glyphicon-remove"></span></button>'
    }
}

CancelEditButton.prototype = new Button();
CancelEditButton.prototype.constructor = CancelEditButton;


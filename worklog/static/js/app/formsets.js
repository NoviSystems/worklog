function FormSet() {
    this.forms = {};
    this.count = 0;
    var formList = [];

    this.addForm = function(form) {
        this.forms[form.selector] = form;
        formList.push(form);
        this.count++;
    }

    this.getForm = function(selector) {
        return this.forms[selector];
    }

    this.removeForm = function(selector) {
        delete this.forms[selector];
    }

    this.post = function() {
        for (var i in this.forms) {
            if (this.forms[i].selector[1] === 'n')
                this.forms[i].post();
        }
    }

    this.saveWorkItem = function(selector, errorCallback) {
        this.forms[selector].put(errorCallback);
    }

    this.tail = function() {
        return formList[this.count - 2];            
    }
}
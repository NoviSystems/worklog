function FormSet() {
    this.forms = {};
    this.count = 0;
    var formList = [];

    this.addForm = function(form) {
        this.forms[form.selector] = form;
        formList.push(form);
        this.count++;
    };

    this.getForm = function(selector) {
        return this.forms[selector];
    };

    this.removeForm = function(selector) {
        delete this.forms[selector];
    };

    this.post = function() {
        for (var i in this.forms) {
            if (this.forms[i].selector[1] === 'n')
                this.forms[i].post();
            else
                this.forms[i].put();
        }
    };

    this.postOrPut = function(selector) {
        if (selector[1] === 'n') {
            this.forms[selector].post();
        } else {
            this.forms[selector].put();
        }
    };

    this.postWorkItem = function(selector) {
        this.forms[selector].post();
    };

    this.putWorkItem = function(selector) {
        this.forms[selector].put();
    };

    this.tail = function() {
        return formList[this.count - 2];            
    };
}
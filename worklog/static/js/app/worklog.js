window.WorkItemApp = Ember.Application.create();

WorkItemApp.Store = DS.Store.extend();

WorkItemApp.ApplicationAdapter = DS.RESTAdapter.extend({
    namespace: 'worklog/api',
});

WorkItemApp.User = DS.Model.extend({
    username: DS.attr('string'),
    email: DS.attr('string'),
    workitems: DS.hasMany('workitem')
});

WorkItemApp.Job = DS.Model.extend({
    name: DS.attr('string'),
    workitems: DS.hasMany('workitem'),
});

WorkItemApp.Repo = DS.Model.extend({
    github_id: DS.attr('number'),
    name: DS.attr('string'),
    issues: DS.hasMany('issue'),
    workitems: DS.hasMany('workitem')
});

WorkItemApp.Issue = DS.Model.extend({
    github_id: DS.attr('number'),
    title: DS.attr('string'),
    number: DS.attr('number'),
    repo: DS.belongsTo('repo'),
    workitems: DS.hasMany('workitem')
});

WorkItemApp.Workitem = DS.Model.extend({
    user: DS.belongsTo('user'),
    date: DS.attr('date'),
    hours: DS.attr('number'),
    text: DS.attr('string'),
    job: DS.belongsTo('job'),
    repo: DS.belongsTo('repo'),
    issue: DS.belongsTo('issue')
});

Ember.Handlebars.helper('format-date', function(date){
    return moment(date).format('L');
});
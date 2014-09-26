WorkItemApp.Router.reopen({
    rootURL: '/worklog/'
});

WorkItemApp.Router.map(function() {
    this.route('today');
    this.route('workitems');
    this.resource('workitem', { path: '/workitems/:workitem_id' });
    this.route('repos');
    this.resource('repo', { path: '/repos/:repo_github_id' })
});

WorkItemApp.WorkitemsRoute = Ember.Route.extend({
    model: function() {
        return this.store.find('workitem');
    },
});

WorkItemApp.ReposRoute = Ember.Route.extend({
    model: function() {
        return this.store.find('repo');
    }
})



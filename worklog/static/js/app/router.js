WorkItemApp.Router.map(function() {
    this.route('worklog', { path: '/' });
});

WorkItemApp.Router.reopen({
    rootURL: '/worklog/'
});

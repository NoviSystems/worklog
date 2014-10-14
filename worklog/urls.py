from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import ReportView, ChartView, JobDataView, createWorkItem, viewWork, CurrentDateRedirectView, EmberView, HomepageView

from timesheet import TimesheetView

DATEMIN = r'(?P<datemin>\d{4}-\d{2}-\d{2})'
DATEMAX = r'(?P<datemax>\d{4}-\d{2}-\d{2})'
# accepts:  date_date   or   date_   or   _date
DATERANGE1 = '(?:'+DATEMIN+'_'+DATEMAX+'?)'
DATERANGE2 = '(?:_'+DATEMAX+')'

USERNAME = r'(?P<username>[a-zA-Z0-9]+)'
##JOBID = r'(?:_job_(?P<jobid>[0-9]+))'

urlpatterns = patterns('worklog',
    url(r'^$', login_required(HomepageView.as_view()), {}, name='worklog-home'),
    #(r'^$', CurrentDateRedirectView.as_view(), {}, 'worklog-home'),
    (r'^(?P<date>\d{4}-\d{2}-\d{2})/$', login_required(createWorkItem), {}, 'worklog-date'),
    (r'^today/$', CurrentDateRedirectView.as_view(), {}, 'worklog-today'),
    (r'^add/$', CurrentDateRedirectView.as_view(), {}, 'worklog-add'),

    (r'^view/$', login_required(viewWork)),
    #(r'^view/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/today/$', login_required(viewWork), {'datemin': 'today', 'datemax': 'today'}),

    (r'^view/'+DATERANGE1+'/$', login_required(viewWork)),
    (r'^view/'+DATERANGE2+'/$', login_required(viewWork)),
    (r'^view/'+USERNAME+'/$', login_required(viewWork)),
    #(r'^view/'+USERNAME+'/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/'+USERNAME+'/today/$', login_required(viewWork), {'datemin': 'today', 'datemax': 'today'}),
    (r'^view/'+USERNAME+'/'+DATERANGE1+'/$', login_required(viewWork)),
    (r'^view/'+USERNAME+'/'+DATERANGE2+'/$', login_required(viewWork)),

    (r'^api/', include('worklog.api.urls')),

    (r'^$', EmberView.as_view(), {}, 'ember-view'),
)

urlpatterns += patterns('worklog',
    url(r'^pdf/(?P<payroll_id>\d+)/(?P<employee_id>\d+)/$', 'timesheet.make_pdf', {}, 'make_pdf_url'),
    url(r'^timesheet/$', login_required(TimesheetView.as_view()), name='timesheet_url'),
    url(r'^report/$', login_required(ReportView.as_view()), name='report_url'),
    url(r'^chart/$', login_required(ChartView.as_view()), name='chart_url'),
    url(r'^chart/job/$', login_required(JobDataView.as_view()), name='job_data_url')
)

urlpatterns += staticfiles_urlpatterns()

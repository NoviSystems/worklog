from django.conf.urls import include, patterns, url
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import ReportView, ChartView, JobDataView, WorkItemView, WorklogView, CurrentDateRedirectView, HomepageView
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
    (r'^(?P<date>\d{4}-\d{2}-\d{2})/$', login_required(WorkItemView.as_view()), {}, 'worklog-date'),
    (r'^today/$', CurrentDateRedirectView.as_view(), {}, 'worklog-today'),
    (r'^add/$', CurrentDateRedirectView.as_view(), {}, 'worklog-add'),

    (r'^view/$', login_required(WorklogView.as_view()), {}, 'worklog-view'),
    #(r'^view/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/today/$', login_required(WorklogView.as_view()), {'datemin': 'today', 'datemax': 'today'}, 'worklog-view-today'),

    (r'^view/'+DATERANGE1+'/$', login_required(WorklogView.as_view()), {}, 'worklog-view-daterange'),
    (r'^view/'+DATERANGE2+'/$', login_required(WorklogView.as_view()), {}, 'worklog-view-datemax'),
    (r'^view/'+USERNAME+'/$', login_required(WorklogView.as_view()), {}, 'worklog-view-user'),
    #(r'^view/'+USERNAME+'/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/'+USERNAME+'/today/$', login_required(WorklogView.as_view()), {'datemin': 'today', 'datemax': 'today'}, 'worklog-view-user-today'),
    (r'^view/'+USERNAME+'/'+DATERANGE1+'/$', login_required(WorklogView.as_view()), {}, 'worklog-view-user-daterange'),
    (r'^view/'+USERNAME+'/'+DATERANGE2+'/$', login_required(WorklogView.as_view()), {}, 'worklog-view-user-datemax'),

    (r'^api/', include('worklog.api.urls')),
)

urlpatterns += patterns('worklog',
    url(r'^pdf/(?P<payroll_id>\d+)/(?P<employee_id>\d+)/$', 'timesheet.make_pdf', {}, 'make_pdf_url'),
    url(r'^timesheet/$', login_required(TimesheetView.as_view()), name='timesheet_url'),
    url(r'^report/$', login_required(ReportView.as_view()), name='report_url'),
    url(r'^chart/$', login_required(ChartView.as_view()), name='chart_url'),
    url(r'^chart/job/$', login_required(JobDataView.as_view()), name='job_data_url')
)

urlpatterns += staticfiles_urlpatterns()

from django.conf.urls import include, patterns, url
from django.contrib.auth.decorators import login_required

from worklog import views

DATEMIN = r'(?P<datemin>\d{4}-\d{2}-\d{2})'
DATEMAX = r'(?P<datemax>\d{4}-\d{2}-\d{2})'
# accepts:  date_date   or   date_   or   _date
DATERANGE1 = '(?:'+DATEMIN+'_'+DATEMAX+'?)'
DATERANGE2 = '(?:_'+DATEMAX+')'

USERNAME = r'(?P<username>[a-zA-Z0-9]+)'
# JOBID = r'(?:_job_(?P<jobid>[0-9]+))'

urlpatterns = patterns(
    'worklog',
    url(r'^$', login_required(views.HomepageView.as_view()), {}, name='home'),
    # (r'^$', CurrentDateRedirectView.as_view(), {}, 'worklog-home'),
    (r'^(?P<date>\d{4}-\d{2}-\d{2})/$', login_required(views.WorkItemView.as_view()), {}, 'date'),
    (r'^today/$', views.CurrentDateRedirectView.as_view(), {}, 'today'),
    (r'^add/$', views.CurrentDateRedirectView.as_view(), {}, 'add'),

    (r'^view/$', login_required(views.WorklogView.as_view()), {}, 'view'),
    # (r'^view/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/today/$', login_required(views.WorklogView.as_view()), {'datemin': 'today', 'datemax': 'today'}, 'view-today'),

    (r'^view/'+DATERANGE1+'/$', login_required(views.WorklogView.as_view()), {}, 'view-daterange'),
    (r'^view/'+DATERANGE2+'/$', login_required(views.WorklogView.as_view()), {}, 'view-datemax'),
    (r'^view/'+USERNAME+'/$', login_required(views.WorklogView.as_view()), {}, 'view-user'),
    # (r'^view/'+USERNAME+'/today/$', 'views.viewWork', {'datemin': datetime.date.today(), 'datemax': datetime.date.today()}),
    (r'^view/'+USERNAME+'/today/$', login_required(views.WorklogView.as_view()), {'datemin': 'today', 'datemax': 'today'}, 'view-user-today'),
    (r'^view/'+USERNAME+'/'+DATERANGE1+'/$', login_required(views.WorklogView.as_view()), {}, 'view-user-daterange'),
    (r'^view/'+USERNAME+'/'+DATERANGE2+'/$', login_required(views.WorklogView.as_view()), {}, 'view-user-datemax'),

    (r'^api/', include('worklog.api.urls')),
)

urlpatterns += patterns(
    'worklog',
    url(r'^report/$', login_required(views.ReportView.as_view()), name='report_url'),
    url(r'^chart/$', login_required(views.ChartView.as_view()), name='chart_url'),
    url(r'^chart/job/$', login_required(views.JobDataView.as_view()), name='job_data_url')
)

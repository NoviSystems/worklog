from django.conf.urls import include, url

from worklog import views


DATEMIN = r'(?P<datemin>\d{4}-\d{2}-\d{2})'
DATEMAX = r'(?P<datemax>\d{4}-\d{2}-\d{2})'
# accepts:  date_date   or   date_   or   _date
DATERANGE1 = '(?:' + DATEMIN + '_' + DATEMAX + '?)'
DATERANGE2 = '(?:_' + DATEMAX + ')'

USERNAME = r'(?P<username>[a-zA-Z0-9]+)'
# JOBID = r'(?:_job_(?P<jobid>[0-9]+))'


app_name = 'worklog'

urlpatterns = [
    url(r'^$', views.HomepageView.as_view(), {}, name='home'),
    url(r'^(?P<date>\d{4}-\d{2}-\d{2})/$', views.WorkItemView.as_view(), name='date'),
    url(r'^today/$', views.CurrentDateRedirectView.as_view(), name='today'),
    url(r'^add/$', views.CurrentDateRedirectView.as_view(), name='add'),

    url(r'^view/$', views.WorklogView.as_view(), {}, name='view'),
    url(r'^view/today/$', views.WorklogView.as_view(), {'datemin': 'today', 'datemax': 'today'}, name='view-today'),

    url(r'^view/' + DATERANGE1 + '/$', views.WorklogView.as_view(), name='view-daterange'),
    url(r'^view/' + DATERANGE2 + '/$', views.WorklogView.as_view(), name='view-datemax'),
    url(r'^view/' + USERNAME + '/$', views.WorklogView.as_view(), name='view-user'),
    url(r'^view/' + USERNAME + '/today/$', views.WorklogView.as_view(), {'datemin': 'today', 'datemax': 'today'}, name='view-user-today'),
    url(r'^view/' + USERNAME + '/' + DATERANGE1 + '/$', views.WorklogView.as_view(), name='view-user-daterange'),
    url(r'^view/' + USERNAME + '/' + DATERANGE2 + '/$', views.WorklogView.as_view(), name='view-user-datemax'),

    url(r'^report/$', views.ReportView.as_view(), name='report_url'),
    url(r'^chart/$', views.ChartView.as_view(), name='chart_url'),
    url(r'^chart/job/$', views.JobDataView.as_view(), name='job_data_url'),

    url(r'^api/', include('worklog.api.urls')),
]

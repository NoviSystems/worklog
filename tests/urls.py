from django.conf.urls import include, url, patterns

urlpatterns = [
   url(r'^worklog/', include('worklog.urls', namespace='worklog')),
 ]

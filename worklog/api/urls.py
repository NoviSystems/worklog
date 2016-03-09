
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from worklog.api import views


router = DefaultRouter()
router.register(r'workdays', views.WorkDayViewSet)
router.register(r'workitems', views.WorkItemViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'repos', views.RepoViewSet)
router.register(r'issues', views.IssueViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

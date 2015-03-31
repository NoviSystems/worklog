
from worklog import models
from worklog.api import filters, serializers
from rest_framework import viewsets

from django.contrib.auth.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    # filter_class = there is no user filter class yet


class WorkDayViewSet(viewsets.ModelViewSet):
    queryset = models.WorkDay.objects.all()
    serializer_class = serializers.WorkDaySerializer
    filter_class = filters.WorkDayFilter


class WorkItemViewSet(viewsets.ModelViewSet):
    queryset = models.WorkItem.objects.all()
    serializer_class = serializers.WorkItemSerializer
    filter_class = filters.WorkItemFilter


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer
    filter_class = filters.JobFilter


class RepoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Repo.objects.all()
    serializer_class = serializers.RepoSerializer
    filter_class = filters.RepoFilter


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Issue.objects.all()
    serializer_class = serializers.IssueSerializer
    filter_class = filters.IssueFilter

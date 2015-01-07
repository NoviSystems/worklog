
from worklog import models, filters
from worklog.api import serializers
from rest_framework import viewsets

from django.contrib.auth.models import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    # filter_class = there is no user filter class yet


class WorkDayViewSet(viewsets.ModelViewSet):
    model = models.WorkDay
    serializer_class = serializers.WorkDaySerializer
    filter_class = filters.WorkDayFilter


class WorkItemViewSet(viewsets.ModelViewSet):
    model = models.WorkItem
    serializer_class = serializers.WorkItemSerializer
    filter_class = filters.WorkItemFilter


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Job
    serializer_class = serializers.JobSerializer
    filter_class = filters.JobFilter


class RepoViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Repo
    serializer_class = serializers.RepoSerializer
    filter_class = filters.RepoFilter


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
    model = models.Issue
    serializer_class = serializers.IssueSerializer
    filter_class = filters.IssueFilter

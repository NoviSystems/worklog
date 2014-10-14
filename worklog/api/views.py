from worklog import models
from worklog.api import serializers, renderers

from rest_framework import viewsets

from django.contrib.auth.models import User
from django.db.models import Q


class WorkDayViewSet(viewsets.ModelViewSet):
    model = models.WorkDay
    serializer_class = serializers.WorkDaySerializer

    def get_queryset(self):
        queryset = models.WorkDay.objects.all()
        date = self.request.QUERY_PARAMS.get('date', None)
        user = self.request.QUERY_PARAMS.get('user', None)

        if date is not None:
            queryset = queryset.filter(date=date)

        if user is not None:
            queryset = queryset.filter(user=user)

        return queryset


class WorkItemViewSet(viewsets.ModelViewSet):
	model = models.WorkItem
	serializer_class = serializers.WorkItemSerializer
	renderer_classes = (renderers.WorkItemJSONRenderer,)

    def get_queryset(self):
        queryset = models.WorkItem.objects.all()
        date = self.request.QUERY_PARAMS.get('date', None)
        user = self.request.QUERY_PARAMS.get('user', None)

        if date is not None:
            queryset = queryset.filter(date=date)

        if user is not None:
            queryset = queryset.filter(user=user)

        return queryset


class UserViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	serializer_class = serializers.UserSerializer
	renderer_classes = (renderers.UserJSONRenderer,)


class JobViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Job
	serializer_class = serializers.JobSerializer
	renderer_classes = (renderers.JobJSONRenderer,)

    def get_queryset(self):
        queryset = models.Job.objects.all()
        date = self.request.QUERY_PARAMS.get('date', None)
        name = self.request.QUERY_PARAMS.get('name', None)
        user = self.request.QUERY_PARAMS.get('user', None)

        if date is not None:
            queryset = models.Job.get_jobs_open_on(date)

        if name is not None:
            queryset = queryset.filter(name=name)

        if user is not None:
            queryset = queryset.filter(Q(users__id=user) | Q(available_all_users=True)).distinct()

        return queryset


class RepoViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Repo
	serializer_class = serializers.RepoSerializer
	renderer_classes = (renderers.RepoJSONRenderer,)

    def get_queryset(self):
        queryset = models.Repo.objects.all()
        name = self.request.QUERY_PARAMS.get('name', None)

        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Issue
	serializer_class = serializers.IssueSerializer
	renderer_classes = (renderers.IssueJSONRenderer,)

    def get_queryset(self):
        queryset = models.Issue.objects.all()
        repo = self.request.QUERY_PARAMS.get('repo', None)

        if repo is not None:
            queryset = queryset.filter(repo=repo)
        return queryset

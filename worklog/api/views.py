from worklog import models
from worklog.api import serializers 
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.contrib.auth.models import User
from django.db.models import Q


@api_view(('GET',))
def api_root(request, format=None):
	return Response({
		'users':reverse('user-list', request=request, format=format),
		'workitems': reverse('workitem-list', request=request, format=format),
	})


class WorkItemViewSet(viewsets.ModelViewSet):
	model = models.WorkItem
	serializer_class = serializers.WorkItemSerializer

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


class JobViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Job
	serializer_class = serializers.JobSerializer

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

	def get_queryset(self):
		queryset = models.Repo.objects.all()
		name = self.request.QUERY_PARAMS.get('name', None)

		if name is not None:
			queryset = queryset.filter(name=name)
		return queryset


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Issue
	serializer_class = serializers.IssueSerializer

	def get_queryset(self):
		queryset = models.Issue.objects.all()
		repo = self.request.QUERY_PARAMS.get('repo', None)

		if repo is not None:
			queryset = queryset.filter(repo=repo)
		return queryset

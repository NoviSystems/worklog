from worklog import models
from worklog.api import serializers 
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.contrib.auth.models import User


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

		if date is not None:
			queryset = queryset.filter(date=date)
		return queryset


class UserViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = User.objects.all()
	serializer_class = serializers.UserSerializer


class JobViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Job.objects.filter(available_all_users=True)
	serializer_class = serializers.JobSerializer


class RepoViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Repo.objects.all()
	serializer_class = serializers.RepoSerializer


class IssueViewSet(viewsets.ReadOnlyModelViewSet):
	model = models.Issue
	serializer_class = serializers.IssueSerializer

	def get_queryset(self):
		queryset = models.Issue.objects.all()
		repo = self.request.QUERY_PARAMS.get('repo', None)

		if repo is not None:
			queryset = queryset.filter(repo=repo)
		return queryset

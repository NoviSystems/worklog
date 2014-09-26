from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.utils.encoders import JSONEncoder
from worklog.api import serializers
from worklog.models import Job, Repo, Issue
from django.contrib.auth.models import User
import json


class CompliantJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        new_ret = {}
        if type(data) is list:
            new_ret = {self.title + 's': data}
        else:
            new_ret = {self.title: data}

        return super(CompliantJSONRenderer, self).render(new_ret, accepted_media_type, renderer_context)


class WorkItemJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):

        users = []
        jobs = []
        repos = []
        issues = []

        if type(data) is not list:
            data = list(data)

        for workitem in data:
            user = User.objects.get(pk=workitem['user'])
            us = serializers.UserSerializer(instance=user)
            users.append(us.data)

            job = Job.objects.get(pk=workitem['job'])
            js = serializers.JobSerializer(instance=job)
            jobs.append(js.data)

            try:
                repo = Repo.objects.get(pk=workitem['repo'])
                rs = serializers.RepoSerializer(instance=repo)
                rs.data['id'] = rs.data['github_id']
                repos.append(rs.data)
            except Repo.DoesNotExist:
                pass

            try:
                issue = Issue.objects.get(pk=workitem['issue'])
                iss = serializers.IssueSerializer(instance=issue)
                iss.data['id'] = iss.data['github_id']
                issues.append(iss.data)
            except Issue.DoesNotExist:
                pass

        new_data = {}
        if len(data) > 1:
            new_data['workitems'] = data
        else:
            new_data['workitem'] = data

        new_data['users'] = users
        new_data['jobs'] = jobs
        new_data['repos'] = repos
        new_data['issues'] = issues

        return super(WorkItemJSONRenderer, self).render(new_data, accepted_media_type, renderer_context)
            


class JobJSONRenderer(CompliantJSONRenderer):

    title = 'job'


class RepoJSONRenderer(CompliantJSONRenderer):

    title = 'repo'


class IssueJSONRenderer(CompliantJSONRenderer):

    title = 'issue'


class UserJSONRenderer(CompliantJSONRenderer):

    title = 'user'


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):

    def get_default_renderer(self, view):
        return CompliantJSONRenderer()

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super(CustomBrowsableAPIRenderer, self).render(data, accepted_media_type, renderer_context)
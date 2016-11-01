from worklog.models import WorkDay, WorkItem, Job, Repo, Issue
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import datetime


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ['id', 'name']


class IssueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issue
        fields = ['github_id', 'title', 'body', 'number', 'repo', 'open', 'assignee', 'url']


class RepoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repo
        fields = ['github_id', 'name', 'url']


class WorkDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkDay
        fields = ['id', 'user', 'date', 'reconciled']

    def validate(self, attrs):

        workday = WorkDay.objects.filter(date=attrs['date'], user=attrs['user'])

        if workday:
            raise serializers.ValidationError("User already has a WorkDay.")

        return attrs


class WorkItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkItem
        fields = ['id', 'user', 'date', 'hours', 'text', 'job', 'repo', 'issue']

    def validate_job(self, value):

        if value is None:
            raise serializers.ValidationError("This field is required.")

        open_jobs = Job.get_jobs_open_on(datetime.date.today())

        try:
            open_jobs.get(name=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Job must be open.")

        return value

    def validate_hours(self, value):

        if not value and value != 0:
            raise serializers.ValidationError("This field is required.")

        if (value % 1 != 0) and (value % 1 % .25 != 0):
            raise serializers.ValidationError("For the love of Satan, 15-minute increments. Please.")
        elif value < 0:
            raise serializers.ValidationError("The whole part of hours must be in N.")

        return value

    def validate_text(self, value):

        if not value:
            raise serializers.ValidationError("This field is required.")

        text_string = value.split(None, 1)

        if text_string[0] == 'commit' and len(text_string) == 1:
            raise serializers.ValidationError("Please specify a commit hash.")

        return value

    def validate(self, data):

        if not data:
            raise serializers.ValidationError("Data is null.")

        issue = data['issue']
        repo = data['repo']

        if issue and issue.repo != repo:
            raise serializers.ValidationError("Issue does not belong to repo.")

        return data

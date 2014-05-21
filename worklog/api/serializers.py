from worklog.models import WorkItem, Job, Repo, Issue
from rest_framework import serializers
from django.contrib.auth.models import User

import datetime


class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model = User
		fields = ('id', 'username', 'email')


class JobSerializer(serializers.ModelSerializer):

	class Meta:
		model = Job
		fields = ('id', 'name')


class IssueSerializer(serializers.ModelSerializer):

	class Meta:
		model = Issue


class RepoSerializer(serializers.ModelSerializer):

	class Meta:
		model = Repo


class WorkItemSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkItem
		fields = ('user', 'date', 'hours', 'text', 'job', 'repo', 'issue')

	def validate_issue(self, attrs, source):
		issue = attrs[source]
		repo = attrs['repo']

		try:
			if issue.repo != repo:
				raise serializers.ValidationError("Issue does not belong to repo.")
		except AttributeError:
			pass
		return attrs

	def validate_hours(self, attrs, source):
		hours = attrs[source]

		if hours % 1 != 0.5 and hours % 1 != 0:
			raise serializers.ValidationError("For the love of Satan, half-hour increments. Please.")
		elif hours < 0:
			raise serializers.ValidationError("The whole part of hours must be in N.")

		return attrs

	def validate_job(self, attrs, source):
		job = attrs[source]

		if job.open_date > datetime.date.today() or job.close_date <= datetime.date.today():
			raise serializers.ValidationError("Job must be open.")

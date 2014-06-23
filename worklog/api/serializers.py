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
		fields = ('id', 'user', 'date', 'hours', 'text', 'job', 'repo', 'issue')

	def validate_job(self, attrs, source):

		if attrs[source] is None:
			raise serializers.ValidationError("This field is required.")

		open_jobs = Job.get_jobs_open_on(datetime.date.today())

		if not open_jobs.get(name=attrs[source]):
			raise serializers.ValidationError("Job must be open.")

		return attrs

	def validate_hours(self, attrs, source):
		hours = attrs[source]

		if not hours and hours != 0:
			raise serializers.ValidationError("This field is required.")

		if hours % 1 != 0.5 and hours % 1 != 0:
			raise serializers.ValidationError("For the love of Satan, half-hour increments. Please.")
		elif hours < 0:
			raise serializers.ValidationError("The whole part of hours must be in N.")

		return attrs

	def validate_issue(self, attrs, source):
		issue = attrs[source]
		repo = attrs['repo']

		try:
			if issue.repo != repo:
				raise serializers.ValidationError("Issue does not belong to repo.")
		except AttributeError:
			pass
		return attrs

	def validate_text(self, attrs, source):
		text = attrs[source]

		if not text:
			raise serializers.ValidationError("This field is required.")

		return attrs

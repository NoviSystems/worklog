from worklog.models import WorkDay, WorkItem, Job, Repo, Issue
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

import datetime
import string


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


class WorkDaySerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkDay

	def validate(self, attrs):

		workday = WorkDay.objects.filter(date=attrs['date'], user=attrs['user'])

		if workday:
			raise serializers.ValidationError("User already has a WorkDay.")

		return attrs


class WorkItemSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkItem
		fields = ('id', 'user', 'date', 'hours', 'text', 'job', 'repo', 'issue')

	def validate_job(self, attrs, source):

		try:
			attrs[source]
		except KeyError:
			raise serializers.ValidationError("Field cannot be NoneType")
		except TypeError:
			raise serializers.ValidationError("No POST data provided")

		if attrs[source] is None:
			raise serializers.ValidationError("This field is required.")

		open_jobs = Job.get_jobs_open_on(datetime.date.today())

		try:
			open_jobs.get(name=attrs[source])
		except ObjectDoesNotExist:
			raise serializers.ValidationError("Job must be open.")

		return attrs

	def validate_hours(self, attrs, source):

		try:
			hours = attrs[source]
		except KeyError:
			raise serializers.ValidationError("Field cannot be NoneType")
		except TypeError:
			raise serializers.ValidationError("No POST data provided")

		if not hours and hours != 0:
			raise serializers.ValidationError("This field is required.")

		if hours % 1 != 0.5 and hours % 1 != 0:
			raise serializers.ValidationError("For the love of Satan, half-hour increments. Please.")
		elif hours < 0:
			raise serializers.ValidationError("The whole part of hours must be in N.")

		return attrs

	def validate_issue(self, attrs, source):
		try:
			issue = attrs[source]
			repo = attrs['repo']
		except KeyError:
			raise serializers.ValidationError("Field cannot be NoneType")
		except TypeError:
			raise serializers.ValidationError("No POST data provided")

		try:
			if issue.repo != repo:
				raise serializers.ValidationError("Issue does not belong to repo.")
		except AttributeError:
			pass

		return attrs

	def validate_text(self, attrs, source):

		try:
			text = attrs[source]
		except KeyError:
			raise serializers.ValidationError("Field cannot be NoneType")
		except TypeError:
			raise serializers.ValidationError("No POST data provided")

		if not text:
			raise serializers.ValidationError("This field is required.")

		text_string = string.split(text)

		if text_string[0] == 'commit' and len(text_string) == 1:
			raise serializers.ValidationError("Please specify a commit hash.")

		return attrs

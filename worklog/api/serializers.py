from worklog.models import WorkItem, Job, Repo, Issue
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
	pk = serializers.Field()

	class Meta:
		model = User
		fields = ('username', 'email')


class JobSerializer(serializers.ModelSerializer):
	pk = serializers.Field()

	class Meta:
		model = Job
		fields = ('name', 'pk')


class IssueSerializer(serializers.ModelSerializer):

	class Meta:
		model = Issue
		fields = ('github_id', 'title', 'number', 'repo')


class RepoSerializer(serializers.ModelSerializer):

	class Meta:
		model = Repo
		fields = ('github_id', 'name')


class WorkItemSerializer(serializers.ModelSerializer):

	class Meta:
		model = WorkItem
		fields = ('user', 'date', 'hours', 'text', 'job', 'repo', 'issue')

	def validate(self, attrs):
		try:
			if attrs['issue'].repo != attrs['repo']:
				raise serializers.ValidationError("Issue does not belong to repo.")
		except AttributeError:
			pass
		return attrs

	def validate_hours(self, attrs, source):
		value = attrs[source]

		if value % 1 != 0.5 and value % 1 != 0:
			raise serializers.ValidationError("Hours must be in half-hour increments.")
		return attrs

import datetime

from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework.serializers import ValidationError
from worklog.api.serializers import WorkItemSerializer
from worklog.models import Job, Repo, Issue
from worklog.tests import factories


class WorkItemSerializerTestCase(APITestCase):

    def setUp(self):
        self.serializer = WorkItemSerializer()

        factories.UserFactory.create_batch(10)
        factories.WorkItemFactory.create_batch(10)
        factories.JobFactory.create_batch(10)
        factories.RepoFactory.create_batch(10)
        factories.IssueFactory.create_batch(10)

        self.jobs = Job.objects.all()
        self.open_jobs = Job.get_jobs_open_on(datetime.date.today())
        self.closed_jobs = Job.objects.exclude(pk__in=self.open_jobs.values_list('pk', flat=True))

        self.repos = list(Repo.objects.all())
        self.issues = list(Issue.objects.all())

        for issue in self.issues:
            if issue.repo != self.repos[0]:
                self.repo_issue_mismatch = {'repo': self.repos[0], 'issue': issue}
                break

    def test_fixtures(self):
        users = list(User.objects.all())
        jobs = list(Job.objects.all())
        repos = list(Repo.objects.all())
        issues = list(Issue.objects.all())

        self.assertNotEqual(users, [])
        self.assertNotEqual(jobs, [])
        self.assertNotEqual(repos, [])
        self.assertNotEqual(issues, [])

    def test_validate_job(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job(None, 'job'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job({}, None))

        attrs = self.serializer.validate_job({'job': self.open_jobs[0]}, 'job')
        self.assertIsNotNone(attrs)

        self.assertRaises(ValidationError, lambda: self.serializer.validate_job({'job': None}, 'job'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_job({'job': self.closed_jobs[0]}, 'job'))

    def test_validate_hours(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours(None, 'hours'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours({}, None))

        attrs = self.serializer.validate_hours({'hours': 13}, 'hours')
        self.assertIsNotNone(attrs)
        attrs = self.serializer.validate_hours({'hours': 13.5}, 'hours')
        self.assertIsNotNone(attrs)

        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours({'hours': None}, 'hours'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours({'hours': -1}, 'hours'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_hours({'hours': 1.3}, 'hours'))

    def test_validate_issue(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_issue(None, 'issue'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_issue({}, None))

        attrs = self.serializer.validate_issue({'repo': self.issues[0].repo, 'issue': self.issues[0]}, 'issue')
        self.assertIsNotNone(attrs)

        self.assertRaises(ValidationError, lambda: self.serializer.validate_issue(self.repo_issue_mismatch, 'issue'))

    def test_validate_text(self):
        self.assertRaises(ValidationError, lambda: self.serializer.validate_text(None, 'text'))
        self.assertRaises(ValidationError, lambda: self.serializer.validate_text({}, None))

        attrs = self.serializer.validate_text({'text': 'foo bar baz qux'}, 'text')
        self.assertIsNotNone(attrs)

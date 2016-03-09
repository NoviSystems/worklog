import datetime
import calendar

from django.test import TestCase
from django.contrib.auth.models import User

from worklog.gh_connect import GitHubConnector

from worklog.models import WorkItem, Job, Repo
from tests import factories

from faker.factory import Factory as FakeFactory
faker = FakeFactory.create()


def get_month_end(d):
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


class WorkItemCommitHashSwapTestCase(TestCase):

    def setUp(self):
        self.ghc = GitHubConnector()
        self.repos = self.ghc.get_all_repos()

        for repo in self.repos:
            new_repo = Repo(github_id=repo.id, name=repo.name)
            new_repo.save()

        factories.UserFactory.create_batch(10)
        factories.JobFactory.create_batch(10)

    def test_commit_hash_swap(self):

        repo = self.repos.pop()
        commit = repo.iter_commits().next()

        repo_obj = Repo()
        repo_obj.github_id = repo.id
        repo_obj.name = repo.name
        repo_obj.save()

        workitem = WorkItem()
        workitem.user = User.objects.all()[0]
        workitem.job = Job.objects.filter(available_all_users=True)[0]
        workitem.hours = 10
        workitem.date = datetime.date.today()
        workitem.repo = repo_obj
        workitem.text = 'commit ' + commit.sha + ' extra text'
        workitem.save()

        self.assertEquals(workitem.text, commit.commit.message + ' extra text')

    def test_no_commit(self):

        for i in range(0, 30):

            repo = Repo.objects.all()[0]
            workitem = WorkItem()
            workitem.user = User.objects.all()[0]
            workitem.job = Job.objects.filter(available_all_users=True)[0]
            workitem.hours = 10
            workitem.date = datetime.date.today()
            workitem.repo = repo
            text = faker.sentence()
            workitem.text = text
            workitem.save()

            self.assertEquals(workitem.text, text)

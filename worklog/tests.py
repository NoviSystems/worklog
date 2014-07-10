import unittest
import datetime
import calendar
import uuid

from django.test import TestCase
from django.core import mail  # for testing email functionality
from django.contrib.auth.models import User
from django.db.models import Q

from gh_connect import GitHubConnector

from models import WorkDay, WorkItem, Job, Repo, Issue
import tasks
import factories

from api.serializers import WorkItemSerializer
from api.views import WorkItemViewSet, JobViewSet, RepoViewSet, IssueViewSet
from rest_framework import status
from rest_framework.request import Request
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase, APIRequestFactory

from faker.factory import Factory as FakeFactory
faker = FakeFactory.create()


class UserLogin_Context(object):
    def __init__(self, client, username, password):
        self.client = client
        self.username = username
        self.password = password

    def __enter__(self):
        self.client.login(username=self.username, password=self.password)

    def __exit__(self, type, value, traceback):
        self.client.logout()


class Worklog_TestCaseBase(TestCase):
    def setUp(self):
        today = datetime.date.today()
        self.today = today
        last_week =     today - datetime.timedelta(days=7)
        last_2week =    today - datetime.timedelta(days=14)
        next_week =     today + datetime.timedelta(days=7)
        self.last_week = last_week
        self.next_week = next_week
        self.yesterday =    self.today - datetime.timedelta(days=1)
        self.tomorrow =     self.today + datetime.timedelta(days=1)
        self.today_minus_2 = self.today - datetime.timedelta(days=2)
        self.today_minus_3 = self.today - datetime.timedelta(days=3)
        
        job = Job.objects.create(name="Job_Today",open_date=today)
        job.save()
        job = Job.objects.create(name="Job_OneDay",open_date=today,close_date=today)
        job.save()
        job = Job.objects.create(name="Job_LastWeek",open_date=last_week)
        job.save()
        job = Job.objects.create(name="Job_LastWeek2",open_date=last_week, close_date=today)
        job.save()
        
        job = Job.objects.create(name="Job_Future",open_date=next_week)
        job.save()
        job = Job.objects.create(name="Job_Old",open_date=last_2week, close_date=last_week)
        job.save()
        
        self.user = User.objects.create_user(username="master", email="master@example.com", password="password")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password")

    def tearDown(self):
        # Clean up all test data.  This does not affect the 'real' database, 
        # only the test database
        Job.objects.all().delete()
        WorkItem.objects.all().delete()
        # Delete all test users.
        self.user.delete()
        self.user2.delete()
        
    # for use in 'with' statements
    def scoped_login(self, username, password):
        return UserLogin_Context(self.client, username, password)


def get_month_end(d):
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


class CreateWorkItem_TestCase(Worklog_TestCaseBase):
        
    def test_basic_get(self):
        with self.scoped_login('master', 'password'):
            response = self.client.get('/worklog/' + str(self.today) + '/')
            
            qs = Job.get_jobs_open_on(self.today)
            
            self.assertEquals(qs.count(),4)
            names = list(job.name for job in qs)
            self.assertTrue("Job_Today" in names)
            self.assertTrue("Job_OneDay" in names)
            self.assertTrue("Job_LastWeek" in names)
            self.assertTrue("Job_LastWeek2" in names)
            
            self.assertEquals(len(response.context['items']),0)
    
    def test_badUser(self):
        uuidstr = '00001111000011110000111100001111'
        id = str(uuid.UUID(uuidstr))
        
        # NOTE: login user does not match user associated with the reminder
        with self.scoped_login(username='master', password='password'):
            response = self.client.get('/worklog/view/{0}/'.format(id))

            self.assertEquals(response.status_code, 404)
            
    def test_previousItemsTable(self):
        job = Job.objects.filter(name="Job_Today")[0]
        item = WorkItem(user=self.user, date=self.today, hours=3, 
                        text='My work today.', job=job)
        item.save()
        
        with self.scoped_login('master', 'password'):
            response = self.client.get('/worklog/' + str(self.today) + '/')

            self.assertEquals(len(response.context['items']),1)
            items = response.context['items']
            
            # order of columns depends on configuration, so just check that they exist
            self.assertTrue(job in items[0])        
            self.assertTrue(self.user in items[0])  
            self.assertTrue(3 in items[0])        


class ViewWork_TestCase(Worklog_TestCaseBase):
    def setUp(self):
        super(ViewWork_TestCase,self).setUp()
        # create some work items
        items = [
            # user, date, hours, text, job
            (self.user, self.today, 1, "item1", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.today, 2, "item2", Job.objects.filter(name="Job_OneDay")[0]),
            (self.user, self.today, 3, "item3", Job.objects.filter(name="Job_LastWeek2")[0]),
            
            (self.user, self.yesterday, 4, "item4", Job.objects.filter(name="Job_OneDay")[0]),
            (self.user, self.tomorrow, 5, "item5", Job.objects.filter(name="Job_LastWeek2")[0]),
            (self.user, self.last_week, 6, "item6", Job.objects.filter(name="Job_Today")[0]),
            
            (self.user2, self.today, 7, "item7", Job.objects.filter(name="Job_Today")[0]),
            ]
        for item in items:
            wi = WorkItem.objects.create(user=item[0], date=item[1], hours=item[2], text=item[3], job=item[4])
            wi.save()
    
    def test_basic(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/')
            self.assertEquals(len(response.context['items']),7)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),0)
    
    def test_badDate(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/9876-22-33_/')
            self.assertEquals(len(response.context['items']),7)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1)
    
    def test_badUser(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/?user=999')
            self.assertEquals(len(response.context['items']),0)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1)
    
    def test_badUser2(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/badusername/')
            self.assertEquals(len(response.context['items']),0)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1)
    
    def test_badJob(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/?job=999')
            self.assertEquals(len(response.context['items']),0)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1)
    
    def test_today(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/today/')
            self.assertEquals(len(response.context['items']),4)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),2)  # 2, one for datemin, one for datemax
            
            i = response.context['column_names'].index('Task')  # Task corresponds to WorkItem.text
            texts = list(x[i] for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3','item7',])
    
    def test_today2(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/?datemin={0}&datemax={0}'.format(self.today))
            self.assertEquals(len(response.context['items']),4)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),2)  # 2, one for datemin, one for datemax
            
            i = response.context['column_names'].index('Task')  # Task corresponds to WorkItem.text
            texts = list(x[i] for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3','item7',])
    
    def test_user(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/user2/')
            self.assertEquals(len(response.context['items']),1)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1) 
            
            i = response.context['column_names'].index('Task')  # Task corresponds to WorkItem.text
            texts = list(x[i] for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item7',])
    
    def test_userToday(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/master/today/')
            self.assertEquals(len(response.context['items']),3)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),3)
            
            i = response.context['column_names'].index('Task')  # Task corresponds to WorkItem.text
            texts = list(x[i] for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3',])
    
    def test_dateRange(self):
        with self.scoped_login(username='master', password='password'):
        
            response = self.client.get('/worklog/view/?datemin={0}&datemax={1}'.format(self.last_week,self.yesterday))
            self.assertEquals(len(response.context['items']),2)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),2)  # 2, one for datemin, one for datemax
            
            i = response.context['column_names'].index('Task')  # Task corresponds to WorkItem.text
            texts = list(x[i] for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item4','item6',])


class SendReminderEmails_TestCase(Worklog_TestCaseBase):
    def setUp(self):
        super(SendReminderEmails_TestCase,self).setUp()
        self.user3 = User.objects.create_user(username="user3", email="user3@example.com", password="password")
        self.user4 = User.objects.create_user(username="user4", email="user4@example.com", password="password")
        self.user5 = User.objects.create_user(username="user5", email="user5@example.com", password="password")
        
    def tearDown(self):
        # Delete all test users.
        self.user3.delete()
        self.user4.delete()
        self.user5.delete()
        super(SendReminderEmails_TestCase,self).tearDown()
        
    def test_basic(self):
        # create some work items
        items = [
            # user, date, hours, text, job
            (self.user, self.today, 1, "item1", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.yesterday, 2, "item2", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.today_minus_2, 3, "item3", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.today_minus_3, 4, "item4", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today, 5, "item5", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.yesterday, 6, "item6", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today_minus_2, 7, "item7", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today_minus_3, 8, "item8", Job.objects.filter(name="Job_Today")[0]),
            (self.user3, self.yesterday, 9, "item9", Job.objects.filter(name="Job_Today")[0]),
            (self.user4, self.last_week, 10, "item10", Job.objects.filter(name="Job_Today")[0]),
            (self.user5, self.tomorrow, 11, "item11", Job.objects.filter(name="Job_Today")[0]),
            ]
        for item in items:
            wi = WorkItem.objects.create(user=item[0], date=item[1], hours=item[2], text=item[3], job=item[4])
            wi.save()
            workday, created = WorkDay.objects.get_or_create(user=item[0], date=item[1])
            workday.reconciled = True
            workday.save()

        # try to send emails
        tasks.send_reminder_emails()

        email_count = {
            1: 6,
            2: 5,
            3: 8,
            4: 11, 
            5: 11,
            6: 0,
            7: 0
        }

        emails_sent = email_count[datetime.date.today().isoweekday()]
        
        self.assertEquals(len(mail.outbox), emails_sent)  # user3, user4, user5
        all_recipients = list(m.to[0] for m in mail.outbox)
        self.assertEquals(len(all_recipients), emails_sent)
        if emails_sent:
            self.assertTrue("user3@example.com" in all_recipients)
            self.assertTrue("user4@example.com" in all_recipients)
            self.assertTrue("user5@example.com" in all_recipients)
        
    def test_empty(self):
        # create some work items
        items = [
            # user, date, hours, text, job
            (self.user, self.today, 1, "item1", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today, 2, "item2", Job.objects.filter(name="Job_Today")[0]),
            (self.user3, self.today, 3, "item3", Job.objects.filter(name="Job_Today")[0]),
            (self.user4, self.today, 4, "item4", Job.objects.filter(name="Job_Today")[0]),
            (self.user5, self.today, 5, "item5", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.yesterday, 6, "item6", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.yesterday, 7, "item7", Job.objects.filter(name="Job_Today")[0]),
            (self.user3, self.yesterday, 8, "item8", Job.objects.filter(name="Job_Today")[0]),
            (self.user4, self.yesterday, 9, "item9", Job.objects.filter(name="Job_Today")[0]),
            (self.user5, self.yesterday, 10, "item10", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.today_minus_2, 11, "item11", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today_minus_2, 12, "item12", Job.objects.filter(name="Job_Today")[0]),
            (self.user3, self.today_minus_2, 13, "item13", Job.objects.filter(name="Job_Today")[0]),
            (self.user4, self.today_minus_2, 14, "item14", Job.objects.filter(name="Job_Today")[0]),
            (self.user5, self.today_minus_2, 15, "item15", Job.objects.filter(name="Job_Today")[0]),
            (self.user, self.today_minus_3, 16, "item16", Job.objects.filter(name="Job_Today")[0]),
            (self.user2, self.today_minus_3, 17, "item17", Job.objects.filter(name="Job_Today")[0]),
            (self.user3, self.today_minus_3, 18, "item18", Job.objects.filter(name="Job_Today")[0]),
            (self.user4, self.today_minus_3, 19, "item19", Job.objects.filter(name="Job_Today")[0]),
            (self.user5, self.today_minus_3, 20, "item20", Job.objects.filter(name="Job_Today")[0]),
            ]

        for item in items:
            wi = WorkItem.objects.create(user=item[0], date=item[1], hours=item[2], text=item[3], job=item[4])
            wi.save()
            workday, created = WorkDay.objects.get_or_create(user=item[0], date=item[1])
            workday.reconciled = True
            workday.save()
        
        # try to send emails
        tasks.send_reminder_emails()
        
        self.assertEquals(len(mail.outbox), 0)
        all_recipients = list(m.to[0] for m in mail.outbox)
        self.assertEquals(len(all_recipients), 0)


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
        
        for repo in self.repos:

            commits = list(repo.iter_commits())
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
            workitem.text = 'commit ' + commits[0].sha + ' extra text'
            workitem.save()

            self.assertEquals(workitem.text, commits[0].commit.message + ' extra text')

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


class ViewSetBaseTestCase(APITestCase):

    def setUp(self):

        self._factory = APIRequestFactory()

        factories.UserFactory.create_batch(10)
        factories.WorkItemFactory.create_batch(10)
        factories.JobFactory.create_batch(10)
        factories.RepoFactory.create_batch(10)
        factories.IssueFactory.create_batch(10)

        self.user_pks = list(User.objects.all().values_list('pk', flat=True))
        self.workitem_pks = list(WorkItem.objects.all().values_list('pk', flat=True))
        self.job_pks = list(Job.get_jobs_open_on(datetime.date.today()).values_list('pk', flat=True))
        self.repo_pks = list(Repo.objects.all().values_list('pk', flat=True))
        self.issue_pks = list(Issue.objects.all().values_list('pk', flat=True))

        auth_user = User.objects.get(pk=self.user_pks[0])
        self.client.force_authenticate(user=auth_user)

    def tearDown(self):

        WorkItem.objects.all().delete()
        Job.objects.all().delete()
        Repo.objects.all().delete()
        Issue.objects.all().delete()

    def test_get_queryset(self, query_params=None, expected_qs=None):

        request = self.factory.get('')
        request.GET = query_params
        drf_request = Request(request)
        self.viewset.request = drf_request
        actual_qs = self.viewset.get_queryset().order_by('pk')
        self.assertEqual(list(actual_qs), list(expected_qs))

    @property
    def factory(self):
        return self._factory

    @property
    def viewset(self):
        raise NotImplementedError("Property must be implemented in subclass.")
    

class WorkItemViewSetTestCase(ViewSetBaseTestCase):

    def setUp(self):

        self._viewset = WorkItemViewSet()

        super(WorkItemViewSetTestCase, self).setUp()
    
    def test_get_queryset(self):

        oldest_workitem = WorkItem.objects.all().order_by('date')[0]
        today = datetime.date.today()
        date_list = [today - datetime.timedelta(days=x) for x in range(0, (oldest_workitem.date - today).days)]

        for date in date_list:
            query_params = {'date': str(date)}
            expected_qs = WorkItem.objects.filter(date=date).order_by('pk')
            super(WorkItemViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

        for user in range(1, 30):
            query_params = {'user': user}
            expected_qs = WorkItem.objects.filter(user=user).order_by('pk')
            super(WorkItemViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

        for date in date_list:
            for user in range(1, 30):
                query_params = {'date': str(date), 'user': user}
                expected_qs = WorkItem.objects.filter(user=user, date=date).order_by('pk')
                super(WorkItemViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

    def test_post(self):

        data = {
            'user': self.user_pks[0], 
            'date': '2014-06-21', 
            'job': self.job_pks[0],
            'hours': 2,
            'text': 'Dieses feld ist erforderlich'
        }

        response = self.client.post('/worklog/api/workitems/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put(self):

        data = {
            'id': 7080,
            'user': self.user_pks[0],
            'date': '2014-06-11',
            'job': self.job_pks[0],
            'hours': 9,
            'text': 'testing severythin news'
        }

        response = self.client.put('/worklog/api/workitems/' + str(data['id']) + '/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = {
            'id': 7080,
            'hours': 10
        }

        response = self.client.put('/worklog/api/workitems/' + str(data['id']) + '/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {
            'id': self.workitem_pks[0],
            'user': self.user_pks[0],
            'date': datetime.date.today(),
            'hours': -3,
            'job': self.job_pks[0],
            'text': 'diese mann ist unter arrest'
        }

        response = self.client.put('/worklog/api/workitems/' + str(data['id']) + '/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get(self):

        workitems = WorkItem.objects.all().values_list('id', flat=True)

        for workitem in workitems:
            response = self.client.get('/worklog/api/workitems/' + str(workitem) + '/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @property
    def viewset(self):
        return self._viewset


class JobViewSetTestCase(ViewSetBaseTestCase):

    def setUp(self):

        self._viewset = JobViewSet()

        super(JobViewSetTestCase, self).setUp()

    def test_get_queryset(self):
        
        oldest_job = Job.objects.all().order_by('open_date')[0]
        today = datetime.date.today()
        date_list = [today - datetime.timedelta(days=x) for x in range(0, (oldest_job.open_date - today).days)]

        for date in date_list:
            query_params = {'date': date}
            expected_qs = Job.get_jobs_open_on(date)
            super(JobViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

        job_names = Job.objects.all().values_list('name', flat=True)

        for name in job_names:
            query_params = {'name': name}
            expected_qs = Job.objects.filter(name=name)
            super(JobViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

        for user in range(1, 30):
            query_params = {'user': user}
            expected_qs = Job.objects.filter(Q(users__id=user) | Q(available_all_users=True)).distinct().order_by('pk')
            super(JobViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

        for date in date_list:
            for name in job_names:
                for user in range(1, 30):
                    query_params = {'date': date, 'name': name, 'user': user}
                    expected_qs = Job.get_jobs_open_on(date)
                    expected_qs = expected_qs.filter(name=name)
                    expected_qs = expected_qs.filter(Q(users__id=user) | Q(available_all_users=True)).distinct().order_by('pk')
                    super(JobViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

    def test_post(self):
        
        data = {
            'id': 7114,
            'user': 29,
            'date': '2014-06-23',
            'hours': 3,
            'text': 'testing zero hours',
            'job': self.job_pks[0],
        }

        response = self.client.post('/worklog/api/jobs/' + str(data['id']) + '/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):

        data = {
            'id': 7114,
            'user': self.user_pks[0],
            'date': '2014-06-23',
            'hours': 3,
            'text': 'testing zero hours',
            'job': self.job_pks[0],
        }

        response = self.client.put('/worklog/api/jobs/' + str(data['id']) + '/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):

        data = {
            'id': self.job_pks[3],
            'name': 'Bad banana on Broadway'
        }

        response = self.client.patch('/worklog/api/jobs/' + str(self.job_pks[3]) + '/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):

        for job in self.job_pks:
            response = self.client.get('/worklog/api/jobs/' + str(job) + '/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @property
    def viewset(self):
        return self._viewset


class RepoViewSetTestCase(ViewSetBaseTestCase):

    def setUp(self):

        self._viewset = RepoViewSet()

        super(RepoViewSetTestCase, self).setUp()

    def test_get_queryset(self):
        
        repo_names = Repo.objects.all().values_list('name', flat=True)

        for name in repo_names:
            query_params = {'name': name}
            expected_qs = Repo.objects.filter(name=name)
            super(RepoViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

    def test_post(self):
        
        for pk in self.repo_pks:
            data = {
                'github_id': pk,
                'name': 'bucket o bits'
            }

            response = self.client.post('/worklog/api/repos/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        
        for pk in self.repo_pks:
            data = {
                'github_id': pk,
                'name': 'renegade nuns on wheels'
            }

            response = self.client.put('/worklog/api/repos/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        
        for pk in self.repo_pks:
            data = {
                'github_id': pk,
                'name': 'beleted'
            }

            response = self.client.patch('/worklog/api/repos/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):
        
        for pk in self.repo_pks:
            response = self.client.get('/worklog/api/repos/' + str(pk) + '/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @property
    def viewset(self):
        return self._viewset


class IssueViewSetTestCase(ViewSetBaseTestCase):

    def setUp(self):

        self._viewset = IssueViewSet()

        super(IssueViewSetTestCase, self).setUp()

    def test_get_queryset(self):

        repos = Repo.objects.all().values_list('github_id', flat=True)

        for repo in repos:
            query_params = {'repo': repo}
            expected_qs = Issue.objects.filter(repo=repo).order_by('pk')
            super(IssueViewSetTestCase, self).test_get_queryset(query_params=query_params, expected_qs=expected_qs)

    def test_post(self):
        
        for pk in self.issue_pks:
            data = {
                'github_id': pk,
                'name': 'bucket o bits'
            }

            response = self.client.post('/worklog/api/issues/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        
        for pk in self.issue_pks:
            data = {
                'github_id': pk,
                'name': 'renegade nuns on wheels'
            }

            response = self.client.put('/worklog/api/issues/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        
        for pk in self.issue_pks:
            data = {
                'github_id': pk,
                'name': 'beleted'
            }

            response = self.client.patch('/worklog/api/issues/' + str(pk) + '/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get(self):

        for pk in self.issue_pks:
            response = self.client.get('/worklog/api/issues/' + str(pk) + '/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @property
    def viewset(self):
        return self._viewset    
        

def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(CreateWorkItem_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(ViewWork_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(SendReminderEmails_TestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(WorkItemSerializerTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(WorkItemViewSetTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(WorkItemCommitHashSwapTestCase))    
    test_suite.addTest(loader.loadTestsFromTestCase(JobViewSetTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(RepoViewSetTestCase))
    test_suite.addTest(loader.loadTestsFromTestCase(IssueViewSetTestCase))
    return test_suite

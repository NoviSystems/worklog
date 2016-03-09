import datetime

from django.contrib.auth.models import User
from django.db.models import Q
import uuid

from rest_framework import status
from rest_framework.request import Request
from rest_framework.test import APITestCase, APIRequestFactory

from faker.factory import Factory as FakeFactory

from worklog.models import WorkItem, Job, Repo, Issue
from tests import factories, WorklogTestCaseBase

from worklog.api.views import WorkItemViewSet, JobViewSet, RepoViewSet, IssueViewSet
from random import randrange


faker = FakeFactory.create()


class ViewSetBaseTestCase(APITestCase):

    def setUp(self):

        self._factory = APIRequestFactory()

        factories.UserFactory.create_batch(10)
        factories.WorkItemFactory.create_batch(10)
        factories.JobFactory.create_batch(10)

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

    def get_queryset(self, query_params=None):

        request = self.factory.get('')
        request.GET = query_params
        drf_request = Request(request)
        self.viewset.request = drf_request
        return self.viewset.get_queryset().order_by('pk')

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
        date_list = [today - datetime.timedelta(days=x) for x in range(0, (today - oldest_workitem.date).days)]

        for date in date_list:
            query_params = {'date': str(date)}
            expected_qs = WorkItem.objects.filter(date=date).order_by('pk')
            response = self.client.get('/worklog/api/workitems/', query_params)
            actual_qs = [value["id"] for value in response.data]
            expected_qs = [value.id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

        for user in range(1, 30):
            query_params = {'user': user}
            expected_qs = WorkItem.objects.filter(user=user).order_by('pk')
            response = self.client.get('/worklog/api/workitems/', query_params)
            actual_qs = [value["id"] for value in response.data]
            expected_qs = [value.id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

        for date in date_list:
            for user in range(1, 30):
                query_params = {'date': str(date), 'user': user}
                expected_qs = WorkItem.objects.filter(user=user, date=date).order_by('pk')
                response = self.client.get('/worklog/api/workitems/', query_params)
                actual_qs = [value["id"] for value in response.data]
                expected_qs = [value.id for value in expected_qs]
                self.assertEqual(list(actual_qs), list(expected_qs))

    def test_post(self):

        data = {
            'user': self.user_pks[0],
            'date': '2014-06-21',
            'job': self.job_pks[0],
            'hours': 2,
            'text': 'Dieses feld ist erforderlich',
            'repo': '',
            'issue': '',
        }

        response = self.client.post('/worklog/api/workitems/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put(self):

        data = {
            'id': 10,
            'user': self.user_pks[0],
            'date': '2014-06-11',
            'job': self.job_pks[0],
            'hours': 9,
            'text': 'testing severythin news',
            'repo': '',
            'issue': '',
        }

        # print "WorkItem Count", WorkItem.objects.values_list("pk", flat=True)

        response = self.client.put('/worklog/api/workitems/' + str(data['id']) + '/', data, format='json')
        # print response.content
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            'id': 10,
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
        date_list = [today - datetime.timedelta(days=x) for x in range(0, (today - oldest_job.open_date).days)]

        for date in date_list:
            expected_qs = Job.get_jobs_open_on(date)
            response = self.client.get('/worklog/api/jobs/', {'date': date})
            actual_qs = [value["id"] for value in response.data]
            expected_qs = [value.id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

        job_names = Job.objects.all().values_list('name', flat=True)

        for name in job_names:
            expected_qs = Job.objects.filter(name=name)
            response = self.client.get('/worklog/api/jobs/', {'name': name})
            actual_qs = [value["id"] for value in response.data]
            expected_qs = [value.id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

        for user in range(1, 30):
            expected_qs = Job.objects.filter(Q(users__id=user) | Q(available_all_users=True)).distinct().order_by('pk')
            response = self.client.get('/worklog/api/jobs/', {'user': user})
            actual_qs = [value["id"] for value in response.data]
            expected_qs = [value.id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

        # make a for loop that pics a random date and random job value
        # then loop through for each user
        for x in range(1, 10):
            random_date = date_list[randrange(len(date_list))]
            random_job = job_names[randrange(len(job_names))]
            for user in range(1, 10):
                query_params = {'date': random_date, 'name': random_job, 'user': user}
                expected_qs = Job.get_jobs_open_on(random_date)
                expected_qs = expected_qs.filter(name=random_job)
                expected_qs = expected_qs.filter(Q(users__id=user) | Q(available_all_users=True)).distinct().order_by('pk')
                response = self.client.get('/worklog/api/jobs/', query_params)
                actual_qs = [value["id"] for value in response.data]
                expected_qs = [value.id for value in expected_qs]
                self.assertEqual(list(actual_qs), list(expected_qs))

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
            expected_qs = Repo.objects.filter(name=name)
            response = self.client.get('/worklog/api/repos/', {'name': name})
            actual_qs = [value["github_id"] for value in response.data]
            expected_qs = [value.github_id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

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
            expected_qs = Issue.objects.filter(repo=repo).order_by('pk')
            response = self.client.get('/worklog/api/issues/', {'repo': repo})
            actual_qs = [value["github_id"] for value in response.data]
            expected_qs = [value.github_id for value in expected_qs]
            self.assertEqual(list(actual_qs), list(expected_qs))

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


class CreateWorkItemTestCase(WorklogTestCaseBase):

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


class ViewWorkTestCase(WorklogTestCaseBase):
    def setUp(self):
        super(ViewWorkTestCase, self).setUp()
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
            self.assertEquals(len(response.context['items']), 7)
            self.assertEquals(response.context['menulink_base'], '')
            self.assertEquals(len(response.context['current_filters']), 0)

    def test_badDate(self):
        with self.scoped_login(username='master', password='password'):

            response = self.client.get('/worklog/view/9876-22-33_/')
            self.assertEquals(len(response.context['items']), 7)
            self.assertNotEquals(response.context['menulink_base'], '')
            self.assertEquals(len(response.context['current_filters']), 1)

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

            texts = list(x.text for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3','item7',])

    def test_today2(self):
        with self.scoped_login(username='master', password='password'):

            response = self.client.get('/worklog/view/?datemin={0}&datemax={0}'.format(self.today))
            self.assertEquals(len(response.context['items']),4)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),2)  # 2, one for datemin, one for datemax

            texts = list(x.text for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3','item7',])

    def test_user(self):
        with self.scoped_login(username='master', password='password'):

            response = self.client.get('/worklog/view/user2/')
            self.assertEquals(len(response.context['items']),1)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),1)

            texts = list(x.text for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item7',])

    def test_userToday(self):
        with self.scoped_login(username='master', password='password'):

            response = self.client.get('/worklog/view/master/today/')
            self.assertEquals(len(response.context['items']),3)
            self.assertNotEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),3)

            texts = list(x.text for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item1','item2','item3',])

    def test_dateRange(self):
        with self.scoped_login(username='master', password='password'):

            response = self.client.get('/worklog/view/?datemin={0}&datemax={1}'.format(self.last_week,self.yesterday))
            self.assertEquals(len(response.context['items']),2)
            self.assertEquals(response.context['menulink_base'],'')
            self.assertEquals(len(response.context['current_filters']),2)  # 2, one for datemin, one for datemax

            texts = list(x.text for x in response.context['items'])
            texts.sort()
            self.assertEqual(texts,['item4','item6',])

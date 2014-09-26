from django_webtest import WebTest
from django.core.urlresolvers import reverse
from datetime import date

from factories import UserFactory, IssueFactory, RepoFactory, WorkItemFactory
from worklog.views import get_past_n_days, find_previous_sunday, get_total_hours_from_workitems
from worklog.models import WorkItem


class HomepageViewTestCase(WebTest):

    def setUp(self):
        self.user = UserFactory(username="test_user")
        self.today = date.today()
        self.workitem1 = WorkItemFactory.create(user=self.user, date=self.today, hours=7.75)
        # create 2 new repos
        self.repos = RepoFactory.create_batch(2)
        # create 2 new issues assigned to the user for each repo
        self.issues_for_repo_1 = IssueFactory.create_batch(2, assignee=self.user, open=True, repo=self.repos[0])
        self.issues_for_repo_2 = IssueFactory.create_batch(2, assignee=self.user, open=True, repo=self.repos[1])

    def test_access(self):
         # Login redirect
        self.assertEqual(self.app.get(reverse("worklog-home")).status_int, 302)
        # Homepage URL
        self.assertEqual(self.app.get(reverse("worklog-home"), user=self.user).status_int, 200)

    def test_content(self):
        response = self.app.get(reverse("worklog-home"), user=self.user)

        ###### Test Work pane ######
        # response.mustcontain("hours worked")  # based on self.workitem1

        ###### Test Github pane ######
        # it is possible that the body might get chopped off if to long.  Therefore, only use first 25 chars
        response.mustcontain(self.issues_for_repo_1[0].body[:25])
        response.mustcontain(self.issues_for_repo_1[1].body[:25])
        response.mustcontain(self.issues_for_repo_2[0].body[:25])
        response.mustcontain(self.issues_for_repo_2[1].body[:25])


class ViewsFunctionsTest(WebTest):

    def test_find_previous_sunday(self):
        test_date = date(2014, 9, 25)
        self.assertEqual(find_previous_sunday(test_date), date(2014, 9, 21))

        test_date = date(2014, 9, 21)
        self.assertEqual(find_previous_sunday(test_date), date(2014, 9, 21))

        test_date = date(2014, 9, 20)
        self.assertEqual(find_previous_sunday(test_date), date(2014, 9, 14))

    def test_get_past_n_days(self):
        # list of dates from 9-7 to 9-1 in descending order
        test_week = [date(2014, 9, i) for i in range(7, 0, -1)]
        self.assertListEqual(get_past_n_days(date(2014, 9, 7)), test_week)

    def test_get_total_hours_from_workitems(self):
        user = UserFactory(username="test_user2")
        WorkItemFactory.create_batch(4, user=user, hours=2)
        items = WorkItem.objects.filter(user=user)
        self.assertEqual(get_total_hours_from_workitems(items), 8.0)

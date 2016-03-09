from django_webtest import WebTest
from django.core.urlresolvers import reverse
from datetime import date
from factories import UserFactory, IssueFactory, RepoFactory, WorkItemFactory, JobFactory
from worklog.views import get_past_n_days, find_previous_saturday, get_total_hours_from_workitems
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
        self.assertEqual(self.app.get(reverse("worklog:home")).status_int, 302)
        # Homepage URL
        self.assertEqual(self.app.get(reverse("worklog:home"), user=self.user).status_int, 200)

    def test_content(self):
        response = self.app.get(reverse("worklog:home"), user=self.user)

        ###### Test Work pane ######
        # response.mustcontain("hours worked")  # based on self.workitem1

        ###### Test Github pane ######
        # it is possible that the body might get chopped off if to long.  Therefore, only use first 25 chars
        response.mustcontain(self.issues_for_repo_1[0].body[:25])
        response.mustcontain(self.issues_for_repo_1[1].body[:25])
        response.mustcontain(self.issues_for_repo_2[0].body[:25])
        response.mustcontain(self.issues_for_repo_2[1].body[:25])


class WorklogViewTestCase(WebTest):

    def setUp(self):
        self.user = UserFactory(username="tester")
        self.user2 = UserFactory(username="testre")
        self.job = JobFactory(name="test1", available_all_users=True)
        self.workitemJ = WorkItemFactory.create(user=self.user, job=self.job, date=date(2015,01,13), hours=8.0)
        self.workitemJ2 = WorkItemFactory.create(user=self.user2, job=self.job, date=date(2015, 01, 13), hours=1.0)
        self.workitemD = WorkItemFactory.create(user=self.user, job=self.job, date=date(2014,12,30), hours=7.0)
        self.workitemD2 = WorkItemFactory.create(user=self.user2, job=self.job, date=date(2014, 12, 30), hours=2.0)
        self.workitemT = WorkItemFactory.create(user=self.user, job=self.job, date=date.today(), hours=3.0)
        self.workitemT2 = WorkItemFactory.create(user=self.user2, job=self.job, date=date.today(), hours=3.5)

    def helper(self, string):
        string = str(string)
        string = string.split("Current query:")[1].split("</table>")[0].replace("\n", "").replace(" ", "")
        string = string[string.find("<td>"):string.rfind("</td>")].replace("</td>", "").replace("<td>", "").replace("<tr>", "").replace("</tr>", "")
        return string

    def test_view(self):
        responseView = self.app.get(reverse("worklog:view"),
                user=self.user)
        rV = str(responseView)
        rVc = self.helper(responseView)

        self.assertEqual(rV.count("<td>tester</td>"), 3)
        self.assertEqual(rV.count("<td>testre</td>"), 3)
        self.assertEqual(rVc, "Showingallworkitems.")

    def test_view_today(self):
        responseViewToday = self.app.get(reverse("worklog:view-today"),
                user=self.user)
        rVT = str(responseViewToday)
        rVTc = self.helper(responseViewToday)

        self.assertEqual(rVT.count("<td>tester</td>"), 1)
        self.assertEqual(rVT.count("<td>testre</td>"), 1)
        self.assertEqual(rVTc, "Dateminimum:" + str(date.today()) + "Datemaximum:" + str(date.today()))

    def test_view_range(self):
        responseViewRange = self.app.get(reverse("worklog:view-daterange", kwargs={'datemin':'2014-12-01', 'datemax':'2015-01-13'}),
                user=self.user)
        rVR = str(responseViewRange)
        rVRc = self.helper(responseViewRange)

        self.assertEqual(rVR.count("<td>tester</td>"), 2)
        self.assertEqual(rVR.count("<td>testre</td>"), 2)
        self.assertEqual(rVRc, "Dateminimum:2014-12-01Datemaximum:2015-01-13")

    def test_view_max(self):
        responseViewMax = self.app.get(reverse("worklog:view-datemax", kwargs={'datemax':date.today()}),
                user=self.user)
        rVM = str(responseViewMax)
        rVMc = self.helper(responseViewMax)

        self.assertEqual(rVM.count("<td>tester</td>"), 3)
        self.assertEqual(rVM.count("<td>testre</td>"), 3)
        datemaxtext = "Datemaximum:" + str(date.today())
        self.assertEqual(rVMc, datemaxtext)

    def test_view_user(self):
        responseViewUser = self.app.get(reverse("worklog:view-user", kwargs={'username':'tester'}),
                user=self.user)
        rVU = str(responseViewUser)[:str(responseViewUser).find("Current query:")]
        rVUc = self.helper(responseViewUser)

        self.assertEqual(rVU.count("<td>tester</td>"), 3)
        self.assertEqual(rVU.count("<td>testre</td>"), 0)
        self.assertEqual(rVUc, "User:tester")

    def test_view_user_today(self):
        responseViewUserToday = self.app.get(reverse("worklog:view-user-today", kwargs={'username':'tester'}),
                user=self.user)
        rVUT = str(responseViewUserToday)[:str(responseViewUserToday).find("Current query:")]
        rVUTc = self.helper(responseViewUserToday)

        self.assertEqual(rVUT.count("<td>tester</td>"), 1)
        self.assertEqual(rVUT.count("<td>testre</td>"), 0)
        self.assertEqual(rVUTc, "User:testerDateminimum:" + str(date.today()) + "Datemaximum:" + str(date.today()))

    def test_view_user_range(self):
        responseViewUserRange = self.app.get(reverse("worklog:view-user-daterange", kwargs={'username':'tester', 'datemin':'2014-12-01', 'datemax':'2015-01-31'}),
                user=self.user)
        rVUR = str(responseViewUserRange)[:str(responseViewUserRange).find("Current query:")]
        rVURc = self.helper(responseViewUserRange)

        self.assertEqual(rVUR.count("<td>tester</td>"), 2)
        self.assertEqual(rVUR.count("<td>testre</td>"), 0)
        self.assertEqual(rVURc, "User:testerDateminimum:2014-12-01Datemaximum:2015-01-31")

    def test_view_user_max(self):
        responseViewUserMax = self.app.get(reverse("worklog:view-user-datemax", kwargs={'username':'tester', 'datemax':'2015-01-31'}),
                user=self.user)
        rVUM = str(responseViewUserMax)[:str(responseViewUserMax).find("Current query:")]
        rVUMc = self.helper(responseViewUserMax)

        self.assertEqual(rVUM.count("<td>tester</td>"), 2)
        self.assertEqual(rVUM.count("<td>testre</td>"), 0)
        self.assertEqual(rVUMc, "User:testerDatemaximum:2015-01-31")


class ViewsFunctionsTest(WebTest):

    def test_find_previous_saturday(self):
        test_date = date(2014, 9, 25)
        self.assertEqual(find_previous_saturday(test_date), date(2014, 9, 20))

        test_date = date(2014, 9, 21)
        self.assertEqual(find_previous_saturday(test_date), date(2014, 9, 20))

        test_date = date(2014, 9, 19)
        self.assertEqual(find_previous_saturday(test_date), date(2014, 9, 13))

    def test_get_past_n_days(self):
        # list of dates from 9-7 to 9-1 in descending order
        test_week = [date(2014, 9, i) for i in range(7, 0, -1)]
        self.assertListEqual(get_past_n_days(date(2014, 9, 7)), test_week)

    def test_get_total_hours_from_workitems(self):
        user = UserFactory(username="test_user2")
        WorkItemFactory.create_batch(4, user=user, hours=2)
        items = WorkItem.objects.filter(user=user)
        self.assertEqual(get_total_hours_from_workitems(items), 8.0)

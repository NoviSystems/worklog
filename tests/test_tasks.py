import datetime

from django.core import mail  # for testing email functionality
from django.contrib.auth.models import User

from worklog.models import WorkDay, WorkItem, Job

import worklog.tasks as tasks
from tests import WorklogTestCaseBase


class SendReminderEmailsTestCase(WorklogTestCaseBase):
    def setUp(self):
        super(SendReminderEmailsTestCase, self).setUp()
        self.user3 = User.objects.create_user(username="user3", email="user3@example.com", password="password")
        self.user4 = User.objects.create_user(username="user4", email="user4@example.com", password="password")
        self.user5 = User.objects.create_user(username="user5", email="user5@example.com", password="password")

    def tearDown(self):
        # Delete all test users.
        self.user3.delete()
        self.user4.delete()
        self.user5.delete()
        super(SendReminderEmailsTestCase, self).tearDown()

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

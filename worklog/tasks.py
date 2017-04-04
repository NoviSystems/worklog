import calendar
import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.template import Template, Context

from celery import shared_task

from worklog.gh_connect import GitHubConnector
from worklog.models import Employee, WorkItem, Job, WorkDay, GithubAlias, Repo, Issue


email_msg = Template("""
This is your friendly reminder to submit a work log for {{ date }}. If
you haven't done so already, you may use the following URL,
but you must do so before it expires on {{ exp_date }}.

URL: {{ url }}

{% if url_list %}
    Remaining unlogged days:
    {% for url in url_list %}
        {{ url }}
    {% endfor %}
{% endif %}
""")


html_email_msg = Template("""
<html>
    <body>
        <br /> This is your friendly reminder to submit a work log for {{ date }}. If
        <br /> you haven't done so already, you may use the following URL,
        <br /> but you must do so before it expires on {{ exp_date }}.
        <p>
        URL: {{ url }}
        </p>
        {% if url_list %}
            <p>
            Remaining unlogged days:
            {% for url in url_list %}
                <br /> {{ url }}
            {% endfor %}
            </p>
        {% endif %}
    </body>
<html>
""")


@shared_task
def generate_invoice(default_date=None):
    if default_date is None:
        default_date = datetime.date.today()
    else:
        default_date = datetime.datetime.strptime(default_date, '%Y-%m-%d').date()

    # cal = calendar.Calendar(0)
    billable_jobs = Job.objects.filter(billing_schedule__date=default_date).exclude(invoiceable=False).distinct()
    send_mail = False

    # continue only if we can bill jobs
    if billable_jobs:
        job_work_items = []

        # loop through all the jobs
        for job in billable_jobs:
            work_items = WorkItem.objects.filter(job=job, invoiced=False, date__lt=default_date) \
                .exclude(job__invoiceable=False).distinct().order_by('date')

            # continue only if we have work items
            if work_items:
                # send email if we have work items
                send_mail = True

                # start at the first work item date
                first_date = work_items[0].date
                last_work_item = work_items.order_by('-date')[0]
                end_date = last_work_item.date

                days = (end_date - first_date).days

                week_of_str = '%s/%s/%s'
                job_msg_str = '\n%s (%s)'

                total_hours = 0
                weekly_work_items = []

                # continue to calculate hours until we reach the end date
                while first_date <= end_date:
                    # used to grab weeks in a month; this will stagger the starting weeks of certain months
                    month = calendar.monthcalendar(first_date.year, first_date.month)

                    for week in month:
                        weekly_hours = 0
                        work_item_msgs = []
                        days = [day for day in week if day != 0]  # we need the first day of the month
                        date = datetime.date(first_date.year, first_date.month, days[0])

                        # if its the first day of the week, set the week of string
                        if date.weekday == 0 or date.day == days[0]:
                            week_of = week_of_str % (date.month, date.day, date.year)
                            work_item_msgs.append(week_of)

                        # calculate the work for each day
                        for day in week:
                            if day != 0:
                                items = work_items.filter(date=date)

                                for item in items:
                                    total_hours += item.hours
                                    weekly_hours += item.hours
                                    work_item_msg = '\t\t%s hours, %s' % (item.hours, item.text)
                                    work_item_msgs.append(work_item_msg)

                                date += datetime.timedelta(days=1)

                        # adjust the first date for loop check and add the weekly hours to the week
                        first_date = date
                        work_item_msgs[0] += ' (%s)' % weekly_hours
                        weekly_work_items.append(work_item_msgs)

                job_work_items.append((job_msg_str % (job.name, total_hours), weekly_work_items,))

    if send_mail:
        sub = 'Invoice'
        date_str = '\n\tDate: Week of %s\n'
        email_msgs = []

        # a list of tuples (job, work items in a month)
        for item in job_work_items:
            job_msgs = []
            job = item[0]
            entries = item[1]

            # a list where the first entry is the week and the rest are work items
            for entry in entries:
                if len(entry) > 1:
                    date = date_str % entry[0]
                    work_item_msgs = []

                    # loop through the work items
                    for work in entry[1:]:
                        work_item_msgs.append(work)

                    job_msgs.append(date + ('\n').join(work_item_msgs))

            email_msgs.append(job + ('').join(job_msgs))

        msg = ('\n\n').join(email_msgs)

        msg += '\n\nReport tools: %s?date=%s' % (settings.SITE_URL + reverse('worklog:report_url'), default_date)

        recipients = []

        for admin in settings.ADMINS:
            recipients.append(admin[1])

        from_email = settings.DEFAULT_FROM_EMAIL
        mail.send_mail(sub, msg, from_email, recipients)


# Generate invoices at 2 AM daily if they are needed
# Crontab in settings.py
@shared_task
def generate_invoice_email():
    default_date = datetime.date.today()
    billable_jobs = Job.objects.filter(billing_schedule__date=default_date).distinct()

    # continue only if we there are jobs to bill
    if billable_jobs:
        sub = 'Invoice'
        msg = 'Report tools: %s?date=%s' % (settings.SITE_URL + reverse('worklog:report_url'), default_date)
        recipients = []
        for admin in settings.ADMINS:
            recipients.append(admin[1])

        from_email = settings.DEFAULT_FROM_EMAIL
        mail.send_mail(sub, msg, from_email, recipients)


def create_reminder_email(email_address, date, date_list=[]):
    expire_days = settings.WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER
    exp_date = date + datetime.timedelta(days=expire_days)
    url = create_reminder_url(date)
    url_list = [create_reminder_url(rem_date) for rem_date in date_list]

    msg = email_msg.render(Context({'url': url, 'url_list': url_list, 'exp_date': str(exp_date), 'date': str(date)}))
    html_msg = html_email_msg.render(Context({'url': url, 'url_list': url_list, 'exp_date': str(exp_date), 'date': str(date)}))

    subj = "Worklog reminder for %s" % str(date)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipients = [email_address]

    email = mail.EmailMultiAlternatives(subj, msg, from_email, recipients)
    email.attach_alternative(html_msg, 'text/html')
    return email


def create_reminder_url(date):
    path = '/worklog/' + str(date) + '/'
    return settings.SITE_URL + path


def get_reminder_dates_for_user(user):
    today = datetime.date.today()
    date_list = [today - datetime.timedelta(days=x) for x in range(0, settings.WORKLOG_EMAIL_REMINDERS_EXPIRE_AFTER)]
    rem_dates = []
    for date in date_list:
        if not WorkDay.objects.filter(user=user, date=date, reconciled=True) and date.isoweekday() in range(1, 6):
            rem_dates.append(date)
    return rem_dates


@shared_task
def send_reminder_emails():
    today = datetime.date.today()
    send_emails = settings.WORKLOG_SEND_REMINDERS and today.isoweekday() in range(1, 6)
    if send_emails:
        email_list = []
        for employee in Employee.objects.all():
            user = employee.user

            if not user.email or not user.is_active:
                continue

            date_list = get_reminder_dates_for_user(user)

            for date in date_list:
                email_list.append(create_reminder_email(user.email, date, date_list))
        if email_list:
            connection = mail.get_connection(fail_silently=False)
            for email in email_list:
                email.connection = connection
                email.send()
    #     print "Reminder emails sent"
    # else:
    #     print "Reminder emails turned off, not sent."


def test_send_reminder_email(username, date=datetime.date.today()):
    # For debugging purposes: sends a reminder email
    user = User.objects.filter(username=username)[0]
    date_list = get_reminder_dates_for_user(user)
    email = create_reminder_email(user.email, date, date_list)
    email.send()


@shared_task
def reconcile_db_with_gh(*args, **kwargs):
    ghc = GitHubConnector()
    repos = ghc.get_all_repos()
    issues = ghc.get_all_issues()

    for repo in repos:
        r = Repo(github_id=repo.id, name=repo.name, url=repo.html_url)
        r.save()

    for issue in issues:
        i = Issue(github_id=issue.id)
        i.title = issue.title
        i.number = issue.number
        i.repo = Repo.objects.get(name=issue.repository[1])
        i.open = not issue.is_closed()
        i.url = issue.html_url
        if issue.assignee:
            try:
                i.assignee = GithubAlias.objects.get(github_name=issue.assignee).user
            except GithubAlias.DoesNotExist:
                print("No GithubAlias with github_name '%s' exists" % issue.assignee)
        else:
            i.assignee = None
        i.body = issue.body
        i.save()

    print("Not only did your task run successfully, but you're damned good looking too.")

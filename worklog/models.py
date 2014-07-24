from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from gh_connect import GitHubConnector
import string


class BiweeklyEmployee(models.Model):
    user = models.ForeignKey(User)
    univ_id = models.CharField(max_length=9, verbose_name='University ID')
    project_num = models.CharField(max_length=255, blank=True, verbose_name='Project #')
    obj_code = models.CharField(max_length=255, blank=True, verbose_name='Obj Code')
    hourly_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def get_timesheet_name(self):
        return '%s, %s' % (self.user.last_name, self.user.first_name,)

    def __unicode__(self):
        return u'%s' % self.user.get_full_name()


class Holiday(models.Model):
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __unicode__(self):
        return u'%s' % (self.description,)


class WorkDay(models.Model):
    user = models.ForeignKey(User, related_name='workdays')
    date = models.DateField()
    reconciled = models.BooleanField(default=False)

    @property
    def workitem_set(self):
        return WorkItem.objects.filter(date=self.date, user=self.user)


class WorkPeriod(models.Model):
    payroll_id = models.CharField(max_length=8)
    start_date = models.DateField()
    end_date = models.DateField()
    due_date = models.DateField()
    pay_day = models.DateField()

    def __unicode__(self):
        return u'%s' % (self.payroll_id,)


class Job(models.Model):
    name = models.CharField(max_length=256)
    # end_date is inclusive, so the duration of a Job is end_date-start_date + 1 day
    # if end_date==None, the Job is still open
    open_date = models.DateField()
    close_date = models.DateField(null=True, blank=True)
    do_not_invoice = models.BooleanField(default=False)
    users = models.ManyToManyField(User, null=True, blank=True)
    available_all_users = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)

    @staticmethod
    def get_jobs_open_on(date):
        return Job.objects.filter(open_date__lte=date).filter(Q(close_date__gte=date) | Q(close_date=None))

    def hasFunding(self):
        return len(self.funding.all()) != 0

    def hasWork(self):
        return len(WorkItem.objects.filter(job=self)) != 0


class Repo(models.Model):
    github_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return unicode(self.name)


class Issue(models.Model):
    github_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256, null=True)
    number = models.IntegerField()
    repo = models.ForeignKey(Repo, related_name='issues')

    def __unicode__(self):
        return unicode(self.number) + u': ' + unicode(self.title)


class BillingSchedule(models.Model):
    job = models.ForeignKey(Job, related_name='billing_schedule')
    date = models.DateField()

    def __unicode__(self):
        return u'Billing for %s' % self.job


class Funding(models.Model):
    job = models.ForeignKey(Job, related_name='funding')
    hours = models.IntegerField()
    date_available = models.DateField()

    def __unicode__(self):
        return u'Funding for %s' % self.job


class WorkItem(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    hours = models.FloatField()
    text = models.TextField()
    job = models.ForeignKey(Job)
    repo = models.ForeignKey(Repo, null=True, blank=True)
    issue = models.ForeignKey(Issue, null=True, blank=True)
    invoiced = models.BooleanField(default=False)
    do_not_invoice = models.BooleanField(default=False)

    # see worklog.admin_filter
    date.year_month_filter = True
    user.user_filter = True
    invoiced.is_invoiced_filter = True

    def __unicode__(self):
        return u'{user} on {date} worked {hours} hours on {item} for job {job}'.format(
            user=self.user, date=self.date, hours=self.hours, item=self.text, job=self.job)

    def save(self, *args, **kwargs):
        if(not self.job.available_all_users):
            if(not self.job.users.filter(id=self.user.id).exists()):
                return

        commit, hash, text = ['', '', '']

        text_string = string.split(self.text)

        if len(text_string) == 2:
            commit = text_string[0]
            hash = text_string[1]
        elif len(text_string) == 1:
            commit = text_string[0]
        else:
            commit, hash, text = string.split(self.text, None, 2)

        # If the text begins with "commit <sha1>", we'll sub in the actual commit message
        if (commit == "commit" and self.repo):

            ghc = GitHubConnector()
            repos = ghc.get_all_repos()

            for repo in repos:
                if repo.id == self.repo.github_id:
                    msg = repo.commit(hash).commit.message
                    self.text = '%s %s' % (msg, text)
                    break

        super(WorkItem, self).save(*args, **kwargs)

import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q, Case, When

from worklog.gh_connect import GitHubConnector

User = settings.AUTH_USER_MODEL


class Employee(models.Model):
    user = models.OneToOneField(User)

    def __str__(self):
        return '%s' % self.user.get_full_name()


class GithubAlias(models.Model):
    user = models.ForeignKey(User)
    github_name = models.CharField(max_length=39, null=True, blank=True)  # 39 is github max


class Holiday(models.Model):
    description = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '%s' % (self.description,)


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

    def __str__(self):
        return '%s' % (self.payroll_id,)


class JobQuerySet(models.QuerySet):
    def annotate_is_open(self, date=None):
        if date is None:
            date = datetime.date.today()
        return self.annotate(is_open=Case(
            When(
                condition=Q(open_date__lte=date) & (Q(close_date__gte=date) | Q(close_date=None)),
                then=True,
            ),
            default=False,
            output_field=models.BooleanField(),
        ))


class JobManager(models.Manager.from_queryset(JobQuerySet)):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate_is_open()


class Job(models.Model):
    name = models.CharField(max_length=256)
    # end_date is inclusive, so the duration of a Job is end_date-start_date + 1 day
    # if end_date==None, the Job is still open
    open_date = models.DateField()
    close_date = models.DateField(null=True, blank=True)
    invoiceable = models.BooleanField(default=True)
    users = models.ManyToManyField(User, blank=True)
    available_all_users = models.BooleanField(default=True)

    objects = JobManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_jobs_open_on(cls, date):
        return cls.objects \
            .annotate_is_open(date) \
            .filter(is_open=True)

    def hasFunding(self):
        return len(self.funding.all()) != 0

    def hasWork(self):
        return len(WorkItem.objects.filter(job=self)) != 0


class Repo(models.Model):
    github_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    url = models.URLField(null=True)

    def __str__(self):
        return self.name


class Issue(models.Model):
    github_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256, null=True)
    body = models.TextField(null=True)
    number = models.IntegerField()
    repo = models.ForeignKey(Repo, related_name='issues')
    open = models.BooleanField(default=False)
    assignee = models.ForeignKey(User, null=True)
    url = models.URLField(null=True)

    def __str__(self):
        return '%d: %s' % (self.number, self.title)


class BillingSchedule(models.Model):
    job = models.ForeignKey(Job, related_name='billing_schedule')
    date = models.DateField()

    def __str__(self):
        return 'Billing for %s' % self.job


class Funding(models.Model):
    job = models.ForeignKey(Job, related_name='funding')
    hours = models.IntegerField()
    date_available = models.DateField()

    def __str__(self):
        return 'Funding for %s' % self.job


class WorkItem(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    hours = models.FloatField()
    text = models.TextField(verbose_name="Tasks")
    job = models.ForeignKey(Job)
    repo = models.ForeignKey(Repo, null=True, blank=True)
    issue = models.ForeignKey(Issue, null=True, blank=True)
    invoiced = models.BooleanField(default=False)

    def __str__(self):
        return '{user} on {date} worked {hours} hours on job {job} doing {item}'.format(
            user=self.user, date=self.date, hours=self.hours, job=self.job, item=self.text)

    def save(self, *args, **kwargs):
        if(not self.job.available_all_users):
            if(not self.job.users.filter(id=self.user.id).exists()):
                raise ValueError("Specified job is not available to {user}".format(user=str(self.user)))

        commit, sha, text = ['', '', '']

        text_string = self.text.split()

        if len(text_string) == 2:
            commit = text_string[0]
            sha = text_string[1]
        elif len(text_string) == 1:
            commit = text_string[0]
        else:
            commit, sha, text = self.text.split(None, 2)

        # If the text begins with "commit <sha1>", we'll sub in the actual commit message
        if (commit == "commit" and self.repo):

            ghc = GitHubConnector()
            repos = ghc.get_all_repos()

            for repo in repos:
                if repo.id == self.repo.github_id:
                    msg = repo.commit(sha).commit.message
                    self.text = '%s %s' % (msg, text)
                    break

        super(WorkItem, self).save(*args, **kwargs)

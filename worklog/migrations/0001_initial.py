# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingSchedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='BiweeklyEmployee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('univ_id', models.CharField(max_length=9, verbose_name=b'University ID')),
                ('project_num', models.CharField(max_length=255, verbose_name=b'Project #', blank=True)),
                ('obj_code', models.CharField(max_length=255, verbose_name=b'Obj Code', blank=True)),
                ('hourly_pay', models.DecimalField(max_digits=5, decimal_places=2)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Funding',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hours', models.IntegerField()),
                ('date_available', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='GithubAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_name', models.CharField(max_length=39, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('github_id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=256, null=True)),
                ('body', models.TextField(null=True)),
                ('number', models.IntegerField()),
                ('open', models.BooleanField(default=False)),
                ('url', models.URLField(null=True)),
                ('assignee', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('open_date', models.DateField()),
                ('close_date', models.DateField(null=True, blank=True)),
                ('do_not_invoice', models.BooleanField(default=False)),
                ('available_all_users', models.BooleanField(default=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('github_id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('url', models.URLField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('reconciled', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='workdays', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('hours', models.FloatField()),
                ('text', models.TextField(verbose_name=b'Tasks')),
                ('invoiced', models.BooleanField(default=False)),
                ('do_not_invoice', models.BooleanField(default=False)),
                ('issue', models.ForeignKey(blank=True, to='worklog.Issue', null=True)),
                ('job', models.ForeignKey(to='worklog.Job')),
                ('repo', models.ForeignKey(blank=True, to='worklog.Repo', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payroll_id', models.CharField(max_length=8)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('due_date', models.DateField()),
                ('pay_day', models.DateField()),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='repo',
            field=models.ForeignKey(related_name='issues', to='worklog.Repo'),
        ),
        migrations.AddField(
            model_name='funding',
            name='job',
            field=models.ForeignKey(related_name='funding', to='worklog.Job'),
        ),
        migrations.AddField(
            model_name='billingschedule',
            name='job',
            field=models.ForeignKey(related_name='billing_schedule', to='worklog.Job'),
        ),
    ]

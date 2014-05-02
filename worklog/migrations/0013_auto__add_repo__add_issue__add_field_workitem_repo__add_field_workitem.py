# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repo'
        db.create_table(u'worklog_repo', (
            ('github_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'worklog', ['Repo'])

        # Adding model 'Issue'
        db.create_table(u'worklog_issue', (
            ('github_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('repo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issue', to=orm['worklog.Repo'])),
        ))
        db.send_create_signal(u'worklog', ['Issue'])

        # Adding field 'WorkItem.repo'
        db.add_column(u'worklog_workitem', 'repo',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['worklog.Repo'], null=True),
                      keep_default=False)

        # Adding field 'WorkItem.issue'
        db.add_column(u'worklog_workitem', 'issue',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['worklog.Issue'], null=True),
                      keep_default=False)


        # Changing field 'WorkItem.hours'
        db.alter_column(u'worklog_workitem', 'hours', self.gf('django.db.models.fields.FloatField')())

    def backwards(self, orm):
        # Deleting model 'Repo'
        db.delete_table(u'worklog_repo')

        # Deleting model 'Issue'
        db.delete_table(u'worklog_issue')

        # Deleting field 'WorkItem.repo'
        db.delete_column(u'worklog_workitem', 'repo_id')

        # Deleting field 'WorkItem.issue'
        db.delete_column(u'worklog_workitem', 'issue_id')


        # Changing field 'WorkItem.hours'
        db.alter_column(u'worklog_workitem', 'hours', self.gf('django.db.models.fields.IntegerField')())

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'worklog.billingschedule': {
            'Meta': {'object_name': 'BillingSchedule'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'billing_schedule'", 'to': u"orm['worklog.Job']"})
        },
        u'worklog.biweeklyemployee': {
            'Meta': {'object_name': 'BiweeklyEmployee'},
            'hourly_pay': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'project_num': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'univ_id': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'worklog.funding': {
            'Meta': {'object_name': 'Funding'},
            'date_available': ('django.db.models.fields.DateField', [], {}),
            'hours': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funding'", 'to': u"orm['worklog.Job']"})
        },
        u'worklog.holiday': {
            'Meta': {'object_name': 'Holiday'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'worklog.issue': {
            'Meta': {'object_name': 'Issue'},
            'github_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issue'", 'to': u"orm['worklog.Repo']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'})
        },
        u'worklog.job': {
            'Meta': {'object_name': 'Job'},
            'available_all_users': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'close_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'do_not_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'open_date': ('django.db.models.fields.DateField', [], {}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'worklog.repo': {
            'Meta': {'object_name': 'Repo'},
            'github_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'worklog.workitem': {
            'Meta': {'object_name': 'WorkItem'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'do_not_invoice': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hours': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoiced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['worklog.Issue']", 'null': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['worklog.Job']"}),
            'repo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['worklog.Repo']", 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'worklog.worklogreminder': {
            'Meta': {'object_name': 'WorkLogReminder'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reminder_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'submitted_jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['worklog.Job']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'worklog.workperiod': {
            'Meta': {'object_name': 'WorkPeriod'},
            'due_date': ('django.db.models.fields.DateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pay_day': ('django.db.models.fields.DateField', [], {}),
            'payroll_id': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        }
    }

    complete_apps = ['worklog']
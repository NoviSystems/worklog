import csv
import io
from collections import Counter
from datetime import date
from operator import attrgetter
from zipfile import ZipFile

from django.contrib import admin, messages
from django.contrib.admin import helpers, SimpleListFilter
from django.db.models import Sum, Q
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django import forms
from django.utils.translation import ugettext_lazy as _

from rangefilter.filter import DateRangeFilter

from worklog.models import WorkItem, Job, BillingSchedule, Funding, GithubAlias, Employee, Holiday, WorkPeriod
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class RelatedFieldListFilter(admin.RelatedFieldListFilter):
    def has_output(self):
        return len(self.lookup_choices) > 0


class DefaultYesFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            (None, _('Yes')),
            ('no', _('No')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class UserIsActiveFilter(DefaultYesFilter):
    title = _('active status')
    parameter_name = 'active'

    def queryset(self, request, queryset):
        if self.value() == 'all':
            return queryset.all()
        # Defaults to show Active Users when all query strings not equal to 'No' or 'All' are passed
        return queryset.filter(is_active=(self.value() != 'no'))


class OpenJobsFilter(DefaultYesFilter):
    title = _('open status')
    parameter_name = 'open'

    def queryset(self, request, queryset):
        if self.value() == 'All':
            return
        # Defaults to show Active Jobs when all query strings not equal to 'No' or 'All' are passed
        return queryset.filter(is_open=(self.value() != 'no'))


class ActiveUserFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False, limit_choices_to={'is_active': True})


class InactiveUserFilter(RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "inactive user"

    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False, limit_choices_to={'is_active': False})


class ActiveJobsFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False, limit_choices_to={'is_open': True})


class InactiveJobsFilter(RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "inactive job"

    def field_choices(self, field, request, model_admin):
        return field.get_choices(include_blank=False, limit_choices_to={'is_open': False})


class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'hours', 'text', 'job', 'invoiceable', 'invoiced', )
    list_filter = (
        ('user', ActiveUserFilter),
        'invoiced', 'job__invoiceable',
        ('date', DateRangeFilter),
        ('job', ActiveJobsFilter),
        ('job', InactiveJobsFilter),
        ('user', InactiveUserFilter),
    )
    actions = ['mark_invoiced', 'mark_not_invoiced', 'archive', 'reassign']
    # sort the items by time in descending order
    ordering = ['-date']

    def mark_invoiced(self, request, queryset):
        queryset.update(invoiced=True)
    mark_invoiced.short_description = "Mark selected items as invoiced"

    def mark_not_invoiced(self, request, queryset):
        queryset.update(invoiced=False)
    mark_not_invoiced.short_description = "Mark selected items as not invoiced"

    def create_invoice(self, job, queryset):
        """
        Generate a CSV name and file for the workitems in the queryset
        """
        labels, getters = zip(*[
            # Title, function on item returning value
            ('Date', attrgetter('date')),
            ('Hours', attrgetter('hours')),
            ('Task', attrgetter('text')),
        ])

        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        dates = []

        writer.writerow(labels)
        for item in queryset.filter(job=job):
            writer.writerow([getter(item) for getter in getters])

            # append year-month date for each item
            dates.append(item.date.strftime('%Y-%m'))

        # generate the file name
        name = "%(name)s-%(year_month)s.csv" % {
            'name': job.name,
            'year_month': Counter(dates).most_common(1)[0][0]
        }

        return name, csvfile.getvalue()

    def archive(self, request, queryset):
        """
        Create a zip of invoices. Each invoice is per job and should contain workitems
        for approximately one month.
        """
        if queryset.filter(job__invoiceable=False).exists():
            self.message_user(request, "Cannot invoice items for jobs that cannot be invoiced.", level=messages.ERROR)
            return
        if queryset.filter(invoiced=True).exists():
            self.message_user(request, "Cannot invoice items that have already been invoiced.", level=messages.ERROR)
            return

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=invoices-%s.zip' % date.today().isoformat()

        with ZipFile(response, 'w') as archive:
            for job in Job.objects.filter(workitem__in=queryset).distinct():
                name, file = self.create_invoice(job, queryset)
                archive.writestr(name, file)

        queryset.update(invoiced=True)

        return response
    archive.short_description = 'Invoice selected items'

    def reassign(self, request, queryset):
        if queryset.filter(invoiced=True).exists():
            self.message_user(request, "Cannot reassign items that have already been invoiced.", level=messages.ERROR)
            return

        if Job.objects.filter(workitem__in=queryset).distinct().count() > 1:
            self.message_user(request, "Cannot simultaneously reassign items from multiple jobs.", level=messages.ERROR)
            return

        today = date.today()
        jobs = Job.objects \
            .filter(Q(open_date__lte=today) & (Q(close_date__isnull=True) | Q(close_date__gte=today))) \
            .exclude(id=queryset.first().job_id)

        if not jobs.exists():
            self.message_user(request, "No other active jobs to reassign work items to.", level=messages.ERROR)
            return

        class Form(forms.Form):
            job = forms.ModelChoiceField(
                label="New job",
                empty_label=None,
                queryset=jobs
            )

        if request.POST.get('post'):
            form = Form(data=request.POST)
            form.is_valid()
            queryset.update(job=form.cleaned_data['job'])

            return None

        return TemplateResponse(request, 'admin/worklog/workitem/reassign.html', dict(
            self.admin_site.each_context(request),
            form=Form(),
            title="Reassign work items",
            queryset=queryset,
            opts=self.model._meta,
            action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            media=self.media,
        ))

    reassign.short_description = 'Reasign selected items to a new job'

    def invoiceable(self, instance):
        return instance.job.invoiceable
    invoiceable.admin_order_field = 'job__invoiceable'
    invoiceable.boolean = True

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            cl = response.context_data['cl']
            hours = cl.get_queryset(request).aggregate(Sum('hours'))
            response.context_data.update(hours)

        return response


class BillingScheduleInline(admin.StackedInline):
    model = BillingSchedule


class FundingInline(admin.StackedInline):
    model = Funding


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_active', )
    list_filter = ('is_staff', 'is_superuser', UserIsActiveFilter, 'groups')


class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'open_date', 'close_date', 'is_open', 'invoiceable')
    list_filter = (OpenJobsFilter,)
    inlines = [
        BillingScheduleInline,
        FundingInline,
    ]

    def is_open(self, obj):
        return obj.is_open

    is_open.boolean = True
    is_open.admin_order_field = 'is_open'


class GithubAliasAdmin(admin.ModelAdmin):
    list_display = ('user', 'github_name')
    ordering = ['user']


class WorkPeriodAdmin(admin.ModelAdmin):
    list_display = ('payroll_id', 'start_date', 'end_date',)
    list_filter = ('start_date', 'end_date',)


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('description', 'start_date', 'end_date',)
    list_filter = ('start_date', 'end_date',)


admin.site.register(WorkItem, WorkItemAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(GithubAlias, GithubAliasAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Employee)
admin.site.register(WorkPeriod, WorkPeriodAdmin)
admin.site.register(Holiday, HolidayAdmin)

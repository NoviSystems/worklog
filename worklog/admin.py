import csv
import io
from collections import Counter
from datetime import date
from operator import attrgetter
from zipfile import ZipFile

from django.contrib import admin, messages
from django.db.models import Sum, Q
from django.http import HttpResponse

from rangefilter.filter import DateRangeFilter

from worklog.models import WorkItem, Job, BillingSchedule, Funding, GithubAlias, Employee, Holiday, WorkPeriod


class RelatedFieldListFilter(admin.RelatedFieldListFilter):
    def has_output(self):
        return len(self.lookup_choices) > 0


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
        today = date.today()
        limit = Q(open_date__lte=today) \
            & (Q(close_date__isnull=True) | Q(close_date__gte=today))

        return field.get_choices(include_blank=False, limit_choices_to=limit)


class InactiveJobsFilter(RelatedFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "inactive job"

    def field_choices(self, field, request, model_admin):
        today = date.today()
        limit = Q(open_date__gt=today) | Q(close_date__lt=today)

        return field.get_choices(include_blank=False, limit_choices_to=limit)


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
    actions = ['mark_invoiced', 'mark_not_invoiced', 'archive']
    # sort the items by time in descending order
    ordering = ['-date']

    def mark_invoiced(self, request, queryset):
        queryset.update(invoiced=True)
    mark_invoiced.short_description = "Mark selected items as invoiced."

    def mark_not_invoiced(self, request, queryset):
        queryset.update(invoiced=False)
    mark_not_invoiced.short_description = "Mark selected items as not invoiced."

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
        if queryset.filter(invoiced=True).exists():
            self.message_user(request, "Cannot invoice items that have already been invoiced.", level=messages.ERROR)
            return

        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=invoices-%s.zip' % date.today().isoformat()

        with ZipFile(response, 'w') as archive:
            for job in Job.objects.filter(workitem__in=queryset):
                name, file = self.create_invoice(job, queryset)
                archive.writestr(name, file)

        queryset.update(invoiced=True)

        return response
    archive.short_description = 'Invoice selected items'

    def invoiceable(self, instance):
        return instance.job.invoiceable
    invoiceable.admin_order_field = 'job__invoiceable'
    invoiceable.boolean = True

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)

        if hasattr(response, 'context_data'):
            cl = response.context_data['cl']
            hours = cl.get_queryset(request).aggregate(Sum('hours'))
            response.context_data.update(hours)

        return response


class BillingScheduleInline(admin.StackedInline):
    model = BillingSchedule


class FundingInline(admin.StackedInline):
    model = Funding


class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'open_date', 'close_date', 'invoiceable')
    inlines = [
        BillingScheduleInline,
        FundingInline,
    ]


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

admin.site.register(Employee)
admin.site.register(WorkPeriod, WorkPeriodAdmin)
admin.site.register(Holiday, HolidayAdmin)

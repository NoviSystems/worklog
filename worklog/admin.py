import csv
import operator
from datetime import date

from django.contrib import admin
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
    actions = ['mark_invoiced', 'mark_not_invoiced']
    # sort the items by time in descending order
    ordering = ['-date']

    def mark_invoiced(self, request, queryset):
        queryset.update(invoiced=True)
    mark_invoiced.short_description = "Mark selected items as invoiced."

    def mark_not_invoiced(self, request, queryset):
        queryset.update(invoiced=False)
    mark_not_invoiced.short_description = "Mark selected items as not invoiced."

    def invoiceable(self, instance):
        return instance.job.invoiceable
    invoiceable.admin_order_field = 'job__invoiceable'
    invoiceable.boolean = True

    # order the job dropdown alphabetically
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "job":
            kwargs["queryset"] = Job.objects.order_by('name')
        return super(WorkItemAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def changelist_view(self, request, extra_context=None):
        # Look for 'export_as_csv' in the HTTP Request header.  If it is found,
        # we export CSV.  If it is not found, defer to the super class.
        if 'export_as_csv' in request.POST:
            def getusername(item):
                if item.user.last_name:
                    return '{0} {1}'.format(item.user.first_name, item.user.last_name)
                # if no first/last name available, fall back to username
                else:
                    return item.user.username

            csvfields = [
                # Title, function on item returning value
                ('User Key', operator.attrgetter('user.pk')),
                ('User Name', getusername),
                ('Job', operator.attrgetter('job.name')),
                ('Date', operator.attrgetter('date')),
                ('Hours', operator.attrgetter('hours')),
                ('Task', operator.attrgetter('text')),
            ]

            ChangeList = self.get_changelist(request)

            # see django/contrib/admin/views/main.py  for ChangeList class.
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links,
                            self.list_filter, self.date_hierarchy, self.search_fields,
                            self.list_select_related, self.list_per_page, self.list_max_show_all,
                            self.list_editable, self)

            header = list(s[0] for s in csvfields)
            rows = [header]
            # Iterate through currently displayed items.
            for item in cl.queryset:
                row = list(s[1](item) for s in csvfields)
                rows.append(row)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=worklog_export.csv'

            writer = csv.writer(response)
            for row in rows:
                writer.writerow(row)

            return response

        else:
            # Get total number of hours for current queryset
            ChangeList = self.get_changelist(request)

            # see django/contrib/admin/views/main.py  for ChangeList class.
            cl = ChangeList(request, self.model, self.list_display, self.list_display_links,
                            self.list_filter, self.date_hierarchy, self.search_fields,
                            self.list_select_related, self.list_per_page, self.list_max_show_all,
                            self.list_editable, self)
        if not extra_context:
            extra_context = cl.get_queryset(request).aggregate(Sum('hours'))
        else:
            extra_context.update(cl.get_queryset(request).aggregate(Sum('hours')))

        return super(WorkItemAdmin, self).changelist_view(request, extra_context)


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


import rest_framework_filters as filters
from worklog import models
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()


class WorkDayFilter(filters.FilterSet):
    class Meta:
        model = models.WorkDay
        fields = ['date', 'user', ]


class WorkItemFilter(filters.FilterSet):
    username = filters.CharFilter(name='user__username', lookup_type='exact')

    class Meta:
        model = models.WorkItem
        fields = {
            'user': ['exact', 'in', ],
            'date': [
                'exact', 'in', 'lt', 'lte', 'gt', 'gte', 'range', 'isnull',
                'year', 'month', 'day', 'week_day',
            ],
            'hours': [
                'exact', 'in', 'lt', 'lte', 'gt', 'gte', 'range',
            ],
            'job': ['exact', 'in', ],
            'repo': ['exact', 'in', 'isnull', ],
            'issue': ['exact', 'in', 'isnull', ],
        }


class JobFilter(filters.FilterSet):

    user = filters.ModelChoiceFilter(method='filter_user', queryset=User.objects.all())
    date = filters.DateFilter(method='filter_date')

    def filter_date(self, qs, name, value):
        return qs.filter(open_date__lte=value).filter(Q(close_date__gte=value) | Q(close_date=None))

    def filter_user(self, qs, name, value):
        if value.is_superuser:
            return qs

        return qs.filter(Q(users__id=value.pk) | Q(available_all_users=True)).distinct()

    class Meta:
        model = models.Job
        fields = {
            'name': ['exact', 'in', ],
        }


class RepoFilter(filters.FilterSet):
    class Meta:
        model = models.Repo
        fields = ['name', ]


class IssueFilter(filters.FilterSet):
    repo = filters.RelatedFilter(RepoFilter, name='repo')

    class Meta:
        model = models.Issue
        fields = ['repo', ]

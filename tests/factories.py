from django.contrib.auth import get_user_model

from worklog.models import WorkItem, Job, Issue, Repo

import random
import factory
from factory.django import DjangoModelFactory
from faker.factory import Factory as FakeFactory

User = get_user_model()
# users = tuple(User.objects.all())
faker = FakeFactory.create()


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    username = factory.LazyAttribute(lambda p: faker.user_name())
    first_name = factory.LazyAttribute(lambda p: faker.first_name())
    last_name = factory.LazyAttribute(lambda p: faker.last_name())
    email = factory.LazyAttribute(lambda p: '{0}.{1}@example.com'.format(p.first_name, p.last_name).lower())
    password = factory.LazyAttribute(lambda p: faker.password())


class JobFactory(DjangoModelFactory):

    class Meta:
        model = Job

    open_date = factory.LazyAttribute(lambda p: faker.date_time_between(start_date='-1y', end_date='-1y'))
    close_date = factory.LazyAttribute(lambda p: faker.date_time_between(start_date='-1y') if random.choice([True, False]) else None)
    name = factory.LazyAttribute(lambda p: faker.sentence(nb_words=3))
    available_all_users = factory.LazyAttribute(lambda p: faker.boolean())

    @factory.post_generation
    def users(self, create, extracted, **kwargs):

        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)


class RepoFactory(DjangoModelFactory):

    class Meta:
        model = Repo

    github_id = factory.Sequence(lambda n: '%04d' % n)
    name = factory.LazyAttribute(lambda p: faker.name())


class IssueFactory(DjangoModelFactory):

    class Meta:
        model = Issue

    github_id = factory.Sequence(lambda n: '%04d' % n)
    title = factory.LazyAttribute(lambda p: faker.name())
    body = factory.LazyAttribute(lambda p: faker.text())
    open = factory.LazyAttribute(lambda p: faker.boolean())
    assignee = factory.SubFactory(UserFactory)
    number = factory.LazyAttribute(lambda p: random.randint(0, 500))
    repo = factory.SubFactory(RepoFactory)


class WorkItemFactory(DjangoModelFactory):

    class Meta:
        model = WorkItem

    user = factory.SubFactory(UserFactory)
    date = factory.LazyAttribute(lambda p: faker.date_time_between(start_date='-1y'))
    job = factory.SubFactory(JobFactory, available_all_users=True)
    hours = factory.LazyAttribute(lambda p: random.randint(1, 24))
    repo = factory.SubFactory(RepoFactory)
    issue = factory.SubFactory(IssueFactory, repo=factory.SelfAttribute('..repo'))
    text = factory.LazyAttribute(lambda p: faker.sentence())

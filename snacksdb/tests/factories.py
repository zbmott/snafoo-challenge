# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from unittest import mock

import factory

from django.contrib.auth.models import User

from snacksdb.models import Ballot, Nomination


class SnacksDBBaseFactory(factory.DjangoModelFactory):
    @classmethod
    def make_in_the_past(cls, when, *pos, **kw):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = when
            return cls(*pos, **kw)


class UserFactory(SnacksDBBaseFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('safe_email')


class BallotFactory(SnacksDBBaseFactory):
    class Meta:
        model = Ballot

    snack_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)


class NominationFactory(SnacksDBBaseFactory):
    class Meta:
        model = Nomination

    snack_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)


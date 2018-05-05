# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

import factory

from django.contrib.auth.models import User

from snacksdb.models import Ballot, Nomination


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('safe_email')


class BallotFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ballot

    snack_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)


class NominationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Nomination

    snack_id = factory.Sequence(lambda n: 1000 + n)
    user = factory.SubFactory(UserFactory)


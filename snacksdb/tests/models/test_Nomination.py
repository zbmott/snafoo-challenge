# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings

from snacksdb.models import Nomination
from snacksdb.tests.factories import NominationFactory, UserFactory


class NominationTestCase(TestCase):
    def test___str__(self):
        nomination = NominationFactory()
        s = str(nomination)

        self.assertIn(nomination.user.username, s)
        self.assertIn(str(nomination.snack_id), s)
        self.assertIn(nomination.created.strftime('%Y-%m-%d %H:%M:%S'), s)

    def test_remaining_in_month_anonymous_user(self):
        self.assertEqual(Nomination.remaining_in_month(AnonymousUser()), 0)

    @override_settings(NOMINATIONS_PER_MONTH=5)
    def test_remaining_in_month_real_users(self):
        user1 = UserFactory()
        user2 = UserFactory()

        self.assertDictEqual(Nomination._remaining_in_month_cache, {})
        self.assertEqual(Nomination.remaining_in_month(user1), 5)
        self.assertEqual(Nomination.remaining_in_month(user2), 5)

        self.assertDictEqual(Nomination._remaining_in_month_cache, {
            user1.pk: 5,
            user2.pk: 5
        })

        NominationFactory(user=user1)

        # Haven't touched the cache yet.
        self.assertEqual(Nomination.remaining_in_month(user1), 5)
        self.assertEqual(Nomination.remaining_in_month(user2), 5)

        for i in range(5):
            NominationFactory(user=user2)

        # Reset the cache
        Nomination._remaining_in_month_cache = {}

        self.assertEqual(Nomination.remaining_in_month(user1), 4)
        self.assertEqual(Nomination.remaining_in_month(user2), 0)

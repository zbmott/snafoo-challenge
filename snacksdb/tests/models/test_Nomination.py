# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from datetime import timedelta
from unittest import mock

from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings

from snacksdb.models import Nomination
from snacksdb.tests.factories import NominationFactory, UserFactory


class NominationTestCase(TestCase):
    """
    Test cases for snacksdb.models.Nomination.
    """
    def setUp(self):
        # If the cache is set up, we need to clear it before running each test,
        # so that cached results from previous tests don't interfer with the
        # current test.
        cache.clear()

    def test_manager_this_month(self):
        """
        Test that the model manager knows a 'this_month' method, and that it returns
        records created during this calendar month.
        """
        nomination1 = NominationFactory()

        end_of_last_month = nomination1.created.replace(day=1) - timedelta(days=1)

        expected_nominations = [
            nomination1,
            NominationFactory(),
            NominationFactory(),
            NominationFactory(user=nomination1.user),
        ]

        # Make historical Nominations. These shouldn't be included in the count.
        NominationFactory.make_in_the_past(end_of_last_month)
        NominationFactory.make_in_the_past(end_of_last_month - timedelta(days=100))

        self.assertEqual(Nomination.objects.this_month().count(), len(expected_nominations))

    def test___str__(self):
        nomination = NominationFactory()
        s = str(nomination)

        self.assertIn(nomination.user.username, s)
        self.assertIn(str(nomination.snack_id), s)
        self.assertIn(nomination.created.strftime('%Y-%m-%d %H:%M:%S'), s)

    def test_remaining_in_month_anonymous_user(self):
        """
        Test that Nomination.remaining_in_month returns 0 for anonymous users.
        """
        self.assertEqual(Nomination.remaining_in_month(AnonymousUser()), 0)

    @override_settings(NOMINATIONS_PER_MONTH=5)
    def test_remaining_in_month_real_users(self):
        """
        Test that Nomination.remaining_in_month correctly counts the
        number of an authenticated user has remaining in the month.
        """
        user1 = UserFactory()
        user2 = UserFactory()

        self.assertEqual(Nomination.remaining_in_month(user1), 5)
        self.assertEqual(Nomination.remaining_in_month(user2), 5)

        NominationFactory(user=user1)
        for i in range(5):
            NominationFactory(user=user2)

        self.assertEqual(Nomination.remaining_in_month(user1), 4)
        self.assertEqual(Nomination.remaining_in_month(user2), 0)

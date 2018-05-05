# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings

from snacksdb.models import Nomination
from snacksdb.tests.factories import NominationFactory, UserFactory


class NominationTestCase(TestCase):
    def test_manager_this_month(self):
        """
        Test that the model manager knows a 'this_month' method, and that it returns
        records created during this calendar month.
        """
        nomination1 = NominationFactory()

        end_of_last_month = Nomination.created.replace(day=1) - timedelta(days=1)

        expected_nominations = [
            nomination1,
            NominationFactory(),
            NominationFactory(),
            NominationFactory(user=nomination1.user),
        ]

        # Mock timezone.now() so that we can create Nominations in the past.
        # DateTimeField.auto_now_add ALWAYS uses timezone.now(), even when
        # you give your own value to the constructor.
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = end_of_last_month
            NominationFactory()
            mock_now.return_value = end_of_last_month - timedelta(days=100)
            NominationFactory()

        self.assertEqual(Nomination.objects.this_month().count(), len(expected_nominations))

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

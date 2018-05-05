# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from datetime import timedelta
from unittest import mock

from django.test import TestCase

from snacksdb.models import Ballot
from snacksdb.tests.factories import BallotFactory


class BallotTestCase(TestCase):
    def test_manager_this_month(self):
        """
        Test that the model manager knows a 'this_month' method, and that it returns
        records created during this calendar month.
        """
        ballot1 = BallotFactory()

        end_of_last_month = ballot1.created.replace(day=1) - timedelta(days=1)

        expected_ballots = [
            ballot1,
            BallotFactory(),
            BallotFactory(),
            BallotFactory(user=ballot1.user),
        ]

        # Mock timezone.now() so that we can create Ballots in the past.
        # DateTimeField.auto_now_add ALWAYS uses timezone.now(), even when
        # you give your own value to the constructor.
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = end_of_last_month
            BallotFactory()
            mock_now.return_value = end_of_last_month - timedelta(days=100)
            BallotFactory()

        self.assertEqual(Ballot.objects.this_month().count(), len(expected_ballots))

    def test___str__(self):
        ballot = BallotFactory()
        s = str(ballot)

        self.assertIn(ballot.user.username, s)
        self.assertIn(str(ballot.snack_id), s)
        self.assertIn(ballot.created.strftime('%Y-%m-%d %H:%M:%S'), s)

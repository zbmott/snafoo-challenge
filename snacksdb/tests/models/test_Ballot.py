# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.test import TestCase

from snacksdb.tests.factories import BallotFactory


class BallotTestCase(TestCase):
    def test___str__(self):
        ballot = BallotFactory()
        s = str(ballot)

        self.assertIn(ballot.user.username, s)
        self.assertIn(str(ballot.snack_id), s)
        self.assertIn(ballot.created.strftime('%Y-%m-%d %H:%M:%S'), s)

# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

import datetime
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from snacksdb.models import Ballot
from snacksdb.tests.factories import BallotFactory, NominationFactory, UserFactory
from snacksdb.utils import get_tzinfo, SnackSourceException
from snacksdb.views import Vote


class VoteTestCase(TestCase):
    """
    Test cases for snacksdb.views.Vote.
    """
    view_url = reverse('snacksdb:vote')

    def setUp(self):
        # If the cache is set up, we need to clear it before running each test,
        # so that cached results from previous tests don't interfer with the
        # current test.
        cache.clear()

    @override_settings(VOTES_PER_MONTH=0)
    def test_post_too_many_votes(self):
        """
        Test that users who have no votes remaining this month can't place additional votes.
        """
        self.client.force_login(UserFactory())
        response = self.client.post(
            reverse('snacksdb:vote'),
            {'snack_id': 1001, 'snack_name': 'Apples'}
        )

        self.assertEqual(response.status_code, 403)

    def test_post_no_snack_id(self):
        """
        Test that 'snack_id' is a required value when submitting a new vote.
        """
        self.client.force_login(UserFactory())
        response = self.client.post(self.view_url, {'snack_name': 'Apples'})
        self.assertEqual(response.status_code, 400)

    def test_post_no_snack_name(self):
        """
        Test that 'snack_name' is a required value when submitting a new vote.
        """
        self.client.force_login(UserFactory())
        response = self.client.post(self.view_url, {'snack_id': 1002})
        self.assertEqual(response.status_code, 400)

    def test_post(self):
        """
        Test that POSTing a valid vote results in a Ballot being created and the
        user being redirected back to 'snacksdb:vote'.
        """
        user = UserFactory()
        self.client.force_login(user)

        ballots_qs = Ballot.objects.filter(user=user)
        self.assertEqual(ballots_qs.count(), 0)

        response = self.client.post(self.view_url, {'snack_id': 1001, 'snack_name': 'Apples'})

        self.assertEqual(ballots_qs.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], self.view_url)

    @override_settings(VOTES_PER_MONTH=5, NOMINATIONS_PER_MONTH=5)
    @mock.patch('snacksdb.views.Vote.fetch_snacks')
    def test_get_context_data(self, mock_fetch):
        view_instance = Vote()
        user = UserFactory()
        view_instance.request = mock.MagicMock(user=user)
        mandatory_snacks = [{'id': 1001 + i} for i in range(3)]
        optional_snacks = [{'id': 1001 + i} for i in range(3, 7)]
        mock_fetch.return_value = (mandatory_snacks, optional_snacks)

        NominationFactory(snack_id=1004, user=user)
        NominationFactory(snack_id=1005, user=user)
        NominationFactory(snack_id=1006)

        BallotFactory(snack_id=1004, user=user)
        BallotFactory(snack_id=1004, user=user)
        BallotFactory(snack_id=1005, user=user)
        BallotFactory(snack_id=1004)

        when = datetime.datetime(2016, 7, 30, 12, 45, 3, tzinfo=get_tzinfo())
        NominationFactory.make_in_the_past(when, snack_id=1004, user=user)
        BallotFactory.make_in_the_past(when, snack_id=1004, user=user)\

        context = view_instance.get_context_data()

        self.assertEqual(context['mandatory_snacks'], mandatory_snacks)
        self.assertEqual(context['optional_snacks'], [
            {'id': 1004, 'total_votes': 3, 'received_vote': True},
            {'id': 1005, 'total_votes': 1, 'received_vote': True},
            {'id': 1006, 'total_votes': 0, 'received_vote': False},
        ])
        self.assertEqual(context['votes_remaining'], 2)
        self.assertEqual(context['nominations_remaining'], 3)

    @mock.patch('snacksdb.utils.SnackAPISource.list')
    def test_fetch_snacks(self, mock_list):
        """
        Test that Vote.fetch_snacks returns a list of mandatory snacks and a
        list of optional snacks, as determined by the snack source.

        Test that if a SnackSourceException is raised, both of these lists
        are empty.
        """
        view_instance = Vote()
        view_instance.request = mock.MagicMock()
        mandatory_snacks = [{'id': 1001 + i, 'optional': False} for i in range(3)]
        optional_snacks = [{'id': 1004 + i, 'optional': True} for i in range(3)]

        mock_list.return_value = mandatory_snacks + optional_snacks

        self.assertEqual(view_instance.fetch_snacks(), (mandatory_snacks, optional_snacks))
        mock_list.assert_called_once()
        mock_list.assert_called_with()

        # Test SnackSourceException error case.
        mock_list.reset_mock()
        mock_list.side_effect = SnackSourceException('oh no!')

        self.assertEqual(view_instance.fetch_snacks(), ([], []))
        mock_list.assert_called_once()
        mock_list.assert_called_with()

    def test_postprocess_optional_snacks(self):
        """
        Test that Vote.postprocess_optional_snacks annonates a list of
        optional snacks with the following information:
          1) The total number of votes that snack has received this month.
          2) Whether or not the current user voted for that snack this month.
        """
        view_instance = Vote()
        user = UserFactory()
        optional_snacks = []

        # Create and nominate snacks.
        for i in range(4):
            snack_id = 1001 + i
            optional_snacks.append({'id': snack_id})
            if snack_id != 1003:  # Don't nominate snack 1003.
                NominationFactory(snack_id=snack_id)

        # Cast the user's ballots.
        user_votes = [
            BallotFactory(snack_id=1001, user=user),
            BallotFactory(snack_id=1001, user=user),
            BallotFactory(snack_id=1002, user=user),
        ]

        # Cast other peoples' ballots.
        for snack_id in [1001, 1002, 1004]:
            BallotFactory(snack_id=snack_id)

        # Cast more ballots (in the past.)
        when = datetime.datetime(2017, 5, 24, 16,30, 21, tzinfo=get_tzinfo())
        BallotFactory.make_in_the_past(when, snack_id=1001, user=user)
        BallotFactory.make_in_the_past(when, snack_id=1003, user=user)
        BallotFactory.make_in_the_past(when, snack_id=1004)

        self.assertListEqual(
            view_instance.postprocess_optional_snacks(optional_snacks, user_votes),
            [
                {'id': 1001, 'total_votes': 3, 'received_vote': True},
                {'id': 1002, 'total_votes': 2, 'received_vote': True},
                {'id': 1004, 'total_votes': 1, 'received_vote': False},
            ]
        )

    def test_filter_unnominated_snacks(self):
        """
        Test that Vote.filter_unnominated_snacks removes snacks that haven't
        been nominated yet this month from the list of optional snacks.
        """
        view_instance = Vote()
        snacks = [{'id': 1001 + i} for i in range(4)]

        # Nominate some snacks.
        for snack_id in [1001, 1001, 1002]:
            NominationFactory(snack_id=snack_id)

        # Nominate a snack in the past.
        when = datetime.datetime(2016, 3, 4, 5, 6, 7, tzinfo=get_tzinfo())
        NominationFactory.make_in_the_past(when, snack_id=1003)

        self.assertEqual(view_instance.filter_unnominated_snacks(snacks), [
            {'id': 1001},
            {'id': 1002},
        ])

    def test_count_votes_by_snack(self):
        """
        Test that Vote.count_votes_by_snack returns a dictionary of
        {snack_id: total_votes_this month, ...} for all snacks.
        """
        view_instance = Vote()
        user = UserFactory()

        # Cast some ballots.
        for i in range(3):
            BallotFactory(snack_id=1001, user=user)
        BallotFactory(snack_id=1002)
        BallotFactory(snack_id=1003)

        # Cast some ballots (in the past).
        when = datetime.datetime(2015, 1, 1, 0, 0, 0, tzinfo=get_tzinfo())
        for snack_id in [1001, 1002, 1003]:
            BallotFactory.make_in_the_past(when, snack_id=snack_id)

        self.assertEqual(view_instance.count_votes_by_snack(), {
            1001: 3,
            1002: 1,
            1003: 1
        })

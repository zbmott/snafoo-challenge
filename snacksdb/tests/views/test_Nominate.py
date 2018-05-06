# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from snacksdb.models import Nomination
from snacksdb.tests.factories import NominationFactory, UserFactory
from snacksdb.utils import SnackSourceException, get_tzinfo
from snacksdb.views import Nominate


class NominateTestCase(TestCase):
    view_url = reverse('snacksdb:nominate')

    def tearDown(self):
        # Reset the cache after each test because other tests might use it.
        Nomination._remaining_in_month_cache = {}

    @mock.patch('snacksdb.views.Nominate.FormView.dispatch')
    def test_dispatch(self, mock_dispatch):
        view_instance = Nominate()
        mock_request = mock.MagicMock(user=UserFactory())

        # Test that a user with no nominations remaining is redirected to views.Vote.
        with override_settings(NOMINATIONS_PER_MONTH=0):
            response = view_instance.dispatch(mock_request)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response['Location'], reverse('snacksdb:vote'))
            mock_dispatch.assert_not_called()

        # Update the user because of Nomination._remaining_in_month_cache.
        mock_request.user = UserFactory()

        # Test that a user with nominations remaining proceeds to the view.
        with override_settings(NOMINATIONS_PER_MONTH=100):
            view_instance.dispatch(mock_request)
            mock_dispatch.assert_called_once()
            mock_dispatch.assert_called_with(mock_request)

    def test_nominate_existing(self):
        user = UserFactory()
        self.client.force_login(user)

        nomination_qs = Nomination.objects.filter(snack_id=1001, user=user)
        self.assertEqual(nomination_qs.count(), 0)

        response = self.client.post(
            self.view_url,
            {
                'snack_id': "{id}{delim}{name}".format(
                    id=1001,
                    delim=Nominate.DELIMITER,
                    name='Apples'
                ),
            }
        )

        self.assertEqual(nomination_qs.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('snacksdb:vote'))

    @mock.patch('snacksdb.utils.SnackAPISource.suggest')
    def test_nominate_new_success(self, mock_suggest):
        user = UserFactory()
        self.client.force_login(user)
        mock_suggest.return_value = {'id': 1002, 'name': 'Bananas'}
        post_data = {'name': 'Bananas', 'location': 'Safeway'}

        nomination_qs = Nomination.objects.filter(snack_id=1002, user=user)
        self.assertEqual(nomination_qs.count(), 0)

        response = self.client.post(self.view_url, post_data)

        mock_suggest.assert_called_once()
        mock_suggest.assert_called_with(latitude=None, longitude=None, **post_data)
        self.assertEqual(nomination_qs.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('snacksdb:vote'))

    @mock.patch('snacksdb.utils.SnackAPISource.list')
    @mock.patch('snacksdb.utils.SnackAPISource.suggest')
    def test_nominate_new_failure(self, mock_suggest, mock_list):
        user = UserFactory()
        self.client.force_login(user)
        post_data = {
            'name': 'Oranges', 'location': 'Food Lion',
            'latitude': 112.87, 'longitude': 0.00
        }

        nomination_qs = Nomination.objects.filter(user=user)
        self.assertEqual(nomination_qs.count(), 0)

        response = self.client.post(self.view_url, post_data)

        mock_suggest.assert_not_called()
        mock_list.assert_called_once()
        self.assertEqual(nomination_qs.count(), 0)
        self.assertEqual(response.status_code, 200)

    @override_settings(NOMINATIONS_PER_MONTH=5)
    @mock.patch('snacksdb.views.Nominate.get_unnominated_snacks')
    def test_get_context_data(self, mock_unnominated_snacks):
        mock_unnominated_snacks.return_value = 'PARTICULARRETURNVALUE'

        # Set up the view instance with a (fake) request and a user.
        view_instance = Nominate()
        view_instance.request = mock.MagicMock(user=UserFactory())
        NominationFactory(user=view_instance.request.user)
        NominationFactory(user=view_instance.request.user)

        context = view_instance.get_context_data()

        self.assertEqual(context['nominations_remaining'], 3)
        self.assertEqual(context['unnominated_snacks'], 'PARTICULARRETURNVALUE')
        self.assertEqual(context['delimiter'], view_instance.DELIMITER)

        mock_unnominated_snacks.assert_called_once()
        mock_unnominated_snacks.assert_called_with()

    @mock.patch('snacksdb.utils.SnackAPISource.list')
    def test_get_unnominated_snacks(self, mock_list):
        view_instance = Nominate()
        mock_list.return_value = [
            {'id': 1001, 'optional': True},
            {'id': 1002, 'optional': False},
            {'id': 1003, 'optional': True},
            {'id': 1004, 'optional': True},
        ]

        # Nominate an optional snack. This one shouldn't in the list.
        NominationFactory(snack_id=1001)

        # Nominate an optional snack a year in the past. This one should be in the list.
        when = timezone.datetime(2017, 1, 1, 0, 0, 0, tzinfo=get_tzinfo())
        NominationFactory.make_in_the_past(when, snack_id=1003)

        # We should only get back snacks that aren't optional and haven't been nominated this month.
        expected_snacks = [
            {'id': 1003, 'optional': True},
            {'id': 1004, 'optional': True},
        ]

        self.assertEqual(view_instance.get_unnominated_snacks(), expected_snacks)

    @mock.patch('snacksdb.views.Nominate.finalize_nomination')
    @mock.patch('snacksdb.views.Nominate.form_invalid')
    @mock.patch('snacksdb.utils.SnackAPISource.suggest')
    def test_form_valid(self, mock_suggest, mock_fi, mock_fn):
        view_instance = Nominate()
        view_instance.request = mock.MagicMock()
        form = mock.MagicMock()

        # Test that Nominate.form_invalid is called when
        # the source raises a SnackSourceException.
        mock_suggest.side_effect = SnackSourceException('exception!')
        view_instance.form_valid(form)
        mock_suggest.assert_called_once()
        mock_fi.assert_called_once()
        mock_fi.assert_called_with(form)
        mock_fn.assert_not_called()

        # Reset the mocks.
        mock_suggest.reset_mock()
        mock_suggest.side_effect = None
        mock_fi.reset_mock()
        mock_fn.reset_mock()

        # Test that Nominate.finalize_nomination is called when no exception is raised.
        mock_suggest.return_value = {'id': 1001, 'name': 'Apples'}
        view_instance.form_valid(form)
        mock_suggest.assert_called_once()
        mock_fn.assert_called_once()
        mock_fn.assert_called_with(1001, 'Apples')
        mock_fi.assert_not_called()

    def test_finalize_nomination(self):
        user = UserFactory()
        view_instance = Nominate()
        view_instance.request = mock.MagicMock(user=user)

        self.assertEqual(Nomination.objects.filter(user=user).count(), 0)

        response = view_instance.finalize_nomination(1001, 'Apples')

        self.assertEqual(Nomination.objects.filter(snack_id=1001, user=user).count(), 1)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('snacksdb:vote'))

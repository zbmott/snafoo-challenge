# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from unittest import mock

from django.test import TestCase, override_settings

from snacksdb.utils import SnackAPISource, SnackSourceException


class SnackAPISourceTestCase(TestCase):
    API_KEY = 'APIKEY'

    def setUp(self):
        self.get_url = SnackAPISource.DEFAULT_API_BASE + SnackAPISource.LIST_PATH
        self.post_url = SnackAPISource.DEFAULT_API_BASE + SnackAPISource.SUGGEST_PATH
        self.headers = {'Authorization': "ApiKey {key}".format(key=self.API_KEY)}
        self.name = 'Apples'
        self.location = 'Giant'

    def test___init__(self):
        # Test 'api_key' parameter
        self.assertEqual(SnackAPISource(api_key='APIKEY').api_key, 'APIKEY')

        with override_settings(SNACK_BACKEND_API_KEY='APIKEY'):
            self.assertEqual(SnackAPISource().api_key, 'APIKEY')

        # Test 'api_base' parameter
        self.assertEqual(SnackAPISource(api_base='APIBASE').api_base, 'APIBASE')

        with override_settings(SNACK_BACKEND_API_BASE='APIBASE'):
            self.assertEqual(SnackAPISource().api_base, 'APIBASE')

        with override_settings(SNACK_BACKEND_API_BASE=None):
            self.assertEqual(SnackAPISource().api_base, SnackAPISource.DEFAULT_API_BASE)

    def test_headers(self):
        api_key = 'APIKEY'
        expected_headers = {'Authorization': "ApiKey {api_key}".format(api_key=api_key)}

        with override_settings(SNACK_BACKEND_API_KEY=api_key):
            self.assertDictEqual(SnackAPISource().headers, expected_headers)

    @mock.patch('requests.get')
    @override_settings(SNACK_BACKEND_API_BASE=None, SNACK_BACKEND_API_KEY=API_KEY)
    def _list_error(self, status_code, mock_get):
        """
        Fake a 'list snacks' GET request, have it return the given status
        code, return the exception it raised. Helper method for testing
        exception behavior in SnackAPISource.list.
        """
        mock_get.return_value = mock.MagicMock(status_code=status_code)

        with self.assertRaises(SnackSourceException) as cm:
            SnackAPISource().list()

        mock_get.assert_called_once()
        mock_get.assert_called_with(self.get_url, headers=self.headers)
        mock_get.return_value.json.assert_not_called()

        return cm.exception

    def test_list_401(self):
        self.assertIn('Access denied', self._list_error(401).msg)

    def test_list_not_200(self):
        self.assertIn('Unknown error', self._list_error(500).msg)

    @mock.patch('requests.get')
    @override_settings(SNACK_BACKEND_API_BASE=None, SNACK_BACKEND_API_KEY=API_KEY)
    def test_list_200(self, mock_get):
        mock_get.return_value = mock.MagicMock(status_code=200)

        try:
            SnackAPISource().list()
        except SnackSourceException:
            self.fail('SnackAPISource.list should not raise an error for response code 200.')

        mock_get.assert_called_once()
        mock_get.assert_called_with(self.get_url, headers=self.headers)
        mock_get.return_value.json.assert_called_once()
        mock_get.return_value.json.assert_called_with()

    @mock.patch('requests.post')
    @override_settings(SNACK_BACKEND_API_BASE=None, SNACK_BACKEND_API_KEY=API_KEY)
    def _post_error(self, status_code, mock_post):
        """
        Fake a 'nominate snack' POST request, have it return the given status
        code, return the exception it raised. Helper method for testing
        exception behavior in SnackAPISource.suggest.
        """
        mock_post.return_value = mock.MagicMock(status_code=status_code)

        with self.assertRaises(SnackSourceException) as cm:
            SnackAPISource().suggest(self.name, self.location)

        mock_post.assert_called_once()
        mock_post.assert_called_with(self.get_url, headers=self.headers, json={
            'name': self.name,
            'location': self.location,
        })
        mock_post.return_value.json.assert_not_called()

        return cm.exception

    def test_suggest_400(self):
        self.assertIn('Malformed suggestion', self._post_error(400).msg)

    def test_suggest_401(self):
        self.assertIn('Access denied', self._post_error(401).msg)

    def test_suggest_409(self):
        self.assertIn('snack already exists', self._post_error(409).msg)

    def test_suggest_not_200(self):
        self.assertIn('Unknown error with Snack API', self._post_error(500).msg)

    @mock.patch('requests.post')
    @override_settings(SNACK_BACKEND_API_BASE=None, SNACK_BACKEND_API_KEY=API_KEY)
    def test_suggest_200(self, mock_post):
        mock_post.return_value = mock.MagicMock(status_code=200)

        # 'included' indicates whether we expect latitude and
        # longitude be included with the request payload.
        test_cases = [
            {'latitude': None, 'longitude': None, 'included': False},
            {'latitude': 40.27, 'longitude': None, 'included': False},
            {'latitude': None, 'longitude': -39.38, 'included': False},
            {'latitude': -89.99, 'longitude': 180.00, 'included': True},
            {'latitude': 0.0, 'longitude': 0.0, 'included': True},
        ]

        for test_case in test_cases:
            # Assemble the expected request payload.
            data = {'name': self.name, 'location': self.location}
            if test_case.pop('included'):
                data.update(test_case)

            # Make the request, assert that it behaved correctly.
            SnackAPISource().suggest(self.name, self.location, **test_case)

            mock_post.assert_called_once()
            mock_post.assert_called_with(self.post_url, headers=self.headers, json=data)
            mock_post.return_value.json.assert_called_once()
            mock_post.return_value.json.assert_called_with()

            # Reset the mocks for the next test case.
            mock_post.reset_mock()
            mock_post.return_value.reset_mock()

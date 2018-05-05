# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

import requests

from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from .AbstractSnackSource import AbstractSnackSource, SnackSourceException


class SnackAPISource(AbstractSnackSource):
    """
    Utility class to wrap raw interactions with the Snack Food API.
    See Snack Food API docs for more information:
    https://api-snacks.nerdery.com/v1/help/
    """
    DEFAULT_API_BASE = 'https://api-snacks.nerderylabs.com/v1'
    LIST_PATH = '/snacks'
    SUGGEST_PATH = '/snacks'

    def __init__(self, api_key=None, api_base=None):
        self.api_key = api_key or settings.SNACK_BACKEND_API_KEY
        self.api_base = api_base or getattr(settings, 'SNACK_BACKEND_API_BASE', None)
        self.api_base = self.api_base or self.DEFAULT_API_BASE

    @cached_property
    def headers(self):
        return {'Authorization': "ApiKey {self.api_key}".format(self=self)}

    def list(self):
        """
        Get a list of available snacks from the Snack Food API.
        """
        response = requests.get(self.api_base + self.LIST_PATH, headers=self.headers)

        # Handle status codes described in the documentation:
        # https://api-snacks.nerderylabs.com/v1/help/api/get-snacks.
        if response.status_code == 401:
            raise SnackSourceException(_('Access denied to Snack API. Check the API key.'))
        elif response.status_code != 200:
            msg = _("Unknown error with Snack API. Maybe it's undergoing maintenance?")
            raise SnackSourceException(msg)

        return response.json()

    def suggest(self, name, location, latitude=None, longitude=None):
        """
        Submit a snack suggestion to the Snack Food API.
        """
        data = {'name': name, 'location': location}
        if latitude is not None and longitude is not None:
            data['latitude'] = float(latitude)
            data['longitude'] = float(longitude)

        response = requests.post(
            self.api_base + self.SUGGEST_PATH,
            headers=self.headers, json=data
        )

        # Handle status codes described in the documentation:
        # https://api-snacks.nerderylabs.com/v1/help/api/post-snacks.
        if response.status_code == 400:
            raise SnackSourceException(_('Malformed suggestion submitted to Snack API.'))
        elif response.status_code == 401:
            raise SnackSourceException(_('Access denied to Snack API. Check the API key.'))
        elif response.status_code == 409:
            raise SnackSourceException(_('Error: That snack already exists!'))
        elif response.status_code != 200:
            msg = _("Unknown error with Snack API (response code {status}). "
                    "Maybe it's undergoing maintenance?")
            raise SnackSourceException(msg.format(status=response.status_code))

        return response.json()

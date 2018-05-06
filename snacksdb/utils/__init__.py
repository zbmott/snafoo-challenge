# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

import pytz

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from .AbstractSnackSource import AbstractSnackSource, SnackSourceException
from .SnackAPISource import SnackAPISource


def get_snack_source():
    """
    Validate settings.SNACK_SOURCE_CLASS and, if valid, return an instance thereof.
    """
    try:
        source_class = import_string(settings.SNACK_SOURCE_CLASS)
    except AttributeError:
        msg = _('settings.SNACK_SOURCE_CLASS must be declared and contain the dotted '
                'path to a class which implements snacksdb.utils.AbstractSnackSource.')
        raise ImproperlyConfigured(msg)
    except ModuleNotFoundError:
        msg = _("Couldn't load settings.SNACK_SOURCE_CLASS. You gave {path}. Check the PYTHONPATH?")
        raise ImproperlyConfigured(msg.format(path=settings.SNACK_SOURCE_CLASS))

    if not issubclass(source_class, AbstractSnackSource):
        msg = _('settings.SNACK_SOURCE_CLASS must refer '
                'to a subclass of AbstractSnackSource.')
        raise ImproperlyConfigured(msg)

    return source_class()


def get_tzinfo(tz_name=None):
    return pytz.timezone(tz_name or settings.TIME_ZONE)

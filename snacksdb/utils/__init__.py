# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from .AbstractSnackSource import SnackSourceException
from .SnackAPISource import SnackAPISource


def get_snack_source():
    try:
        return import_string(settings.SNACK_SOURCE_CLASS)()
    except AttributeError:
        msg = _('settings.SNACK_SOURCE_CLASS must be declared and contain the dotted '
                'path to a class which implements snacksdb.utils.AbstractSnackSource.')
        raise ImproperlyConfigured(msg)
    except ImportError:
        msg = _("Couldn't load settings.SNACK_SOURCE_CLASS. You gave {path}. Check the PYTHONPATH?")
        raise ImproperlyConfigured(msg.format(path=settings.SNACK_SOURCE_CLASS))
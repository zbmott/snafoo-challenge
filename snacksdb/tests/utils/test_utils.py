# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from snacksdb.utils import get_snack_source, SnackAPISource


class UtilsTestCase(TestCase):
    @override_settings()
    def test_snack_source_AttributeError(self):
        # override_settings + 'del settings.SETTING_NAME' is how to delete
        # a setting during testing. See the docs for more information:
        # https://docs.djangoproject.com/en/2.0/topics/testing/tools/#django.test.modify_settings
        del settings.SNACK_SOURCE_CLASS

        with self.assertRaises(ImproperlyConfigured) as cm:
            get_snack_source()

        self.assertIn('settings.SNACK_SOURCE_CLASS must be declared', cm.exception.args[0])

    @override_settings(SNACK_SOURCE_CLASS='path.does.not.exist')
    def test_snack_source_ModuleNotFoundError(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            get_snack_source()

        self.assertIn("Couldn't load settings", cm.exception.args[0])

    @override_settings(SNACK_SOURCE_CLASS='snacksdb.models.Nomination.Nomination')
    def test_snack_source_ImproperlyConfigured(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            get_snack_source()

        self.assertIn('subclass of AbstractSnackSource', cm.exception.args[0])

    @override_settings(SNACK_SOURCE_CLASS='snacksdb.utils.SnackAPISource.SnackAPISource')
    def test_snack_source(self):
        try:
            source = get_snack_source()
        except ImproperlyConfigured:
            self.fail("get_snack_source shouldn't raise an exception when "
                      "SNACK_SOURCE_CLASS refers to SnackAPISource")

        self.assertIsInstance(source, SnackAPISource)

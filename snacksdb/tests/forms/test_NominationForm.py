# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.test import TestCase

from snacksdb.forms import NominationForm


class NominationFormTestCase(TestCase):
    """
    Test cases for snacksdb.forms.NominationForm.
    """
    def generate_test_data(self, **updates):
        """
        Helper method to succintly generate test form data.
        """
        data = {
            'name': 'Apples',
            'location': "Barry's Corner Store"
        }
        
        data.update(updates)
        
        return data

    def test_validation(self):
        """
        Functional test to verify acceptable permutations of
        and values for 'latitude' and 'longitude'.
        """
        test_cases = [
            # Both valid.
            {'latitude': '', 'longitude': '', 'valid': True},
            {'latitude': '0.000', 'longitude': '0.000', 'valid': True},

            # Missing latitude or longitude or longitude.
            {'latitude': '25.783', 'longitude': '', 'valid': False},
            {'latitude': '', 'longitude': '-153.291', 'valid': False},

            # Invalid latitude.
            {'latitude': '-90.001', 'longitude': '-179.999', 'valid': False},
            {'latitude': '90.001', 'longitude': '179.999', 'valid': False},

            # Invalid longitude.
            {'latitude': '-89.999', 'longitude': '-180.001', 'valid': False},
            {'latitude': '89.999', 'longitude': '180.001', 'valid': False},
        ]

        for test_case in test_cases:
            expected_truth = test_case.pop('valid')
            self.assertEqual(
                NominationForm(self.generate_test_data(**test_case)).is_valid(),
                expected_truth
            )

# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from decimal import Decimal as D
from operator import xor

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class NominationForm(forms.Form):
    name = forms.CharField(
        max_length=200, required=True,
        help_text=_('The name of the nominated snack.')
    )
    location = forms.CharField(
        max_length=50, required=True,
        help_text=_('The name of the purchase location.')
    )
    latitude = forms.DecimalField(
        max_digits=10, decimal_places=8, required=False,
        help_text=_('The latitude, in degrees, of the purchase location')
    )
    longitude = forms.DecimalField(
        max_digits=11, decimal_places=8, required=False,
        help_text=_('The longitude, in degrees, of the purchase location')
    )

    def clean_latitude(self):
        latitude = self.cleaned_data['latitude']

        if isinstance(latitude, D) and (latitude < D('-90') or latitude > D('90')):
            raise ValidationError(_('Latitude must be on interval [-90, 90].'))

        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data['longitude']

        if isinstance(longitude, D) and (longitude < D('-180') or longitude > D('180')):
            raise ValidationError(_('Longitude must be on interval [-180, 180].'))

        return longitude

    def clean(self):
        cleaned_data = super().clean()

        # It's invalid to have latitude without longitude, and vice-versa.
        have_latitude = isinstance(cleaned_data.get('latitude'), D)
        have_longitude = isinstance(cleaned_data.get('longitude'), D)

        if xor(have_latitude, have_longitude):
            msg = _('Latitude and longitude must be either both provided or both omitted.')
            raise ValidationError(msg)

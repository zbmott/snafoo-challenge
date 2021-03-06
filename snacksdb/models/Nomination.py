# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .SnacksDBBase import SnacksDBBase


class Nomination(SnacksDBBase):
    """
    Model that represents the snacks a user has nominated.
    Users are allowed to suggest one snack per calendar month.
    """
    MONTHLY_NOMINATIONS_KEY_TMPL = "monthly_nominations_{user_pk}"
    MONTHLY_NOMINATIONS_TTL = 60 * 5

    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name='nominations', help_text=_('User who made the nomination.')
    )
    snack_id = models.PositiveIntegerField(
        verbose_name=_('Snack ID'),
        help_text=_('ID of the nominated snack.'),
    )

    def __str__(self):
        tmpl = ("{self.user.username} nominated snack {self.snack_id} "
                "on {self.created:%Y-%m-%d %H:%M:%S}")
        return tmpl.format(self=self)

    @classmethod
    def get_monthly_nomination_cache_key(cls, user_pk):
        """
        Return the cache key used to store the given user's monthly nomination count.
        """
        return cls.MONTHLY_NOMINATIONS_KEY_TMPL.format(user_pk=user_pk)

    @classmethod
    def remaining_in_month(cls, user):
        """
        Return the number of additional nominations the user has left this month.
        """
        if user.is_anonymous:
            return 0

        cache_key = cls.get_monthly_nomination_cache_key(user.pk)
        cached_value = cache.get(cache_key)

        if cached_value is None:
            user_nominations = cls.objects.this_month().filter(user=user)
            nominations_left = max(0, settings.NOMINATIONS_PER_MONTH - user_nominations.count())
            cache.set(cache_key, nominations_left, cls.MONTHLY_NOMINATIONS_TTL)
            cached_value = nominations_left

        return cached_value

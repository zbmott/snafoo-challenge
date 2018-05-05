# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .SnacksDBBase import SnacksDBBase


class Ballot(SnacksDBBase):
    """
    Model that represents the votes a user has placed for particular snacks.
    users is allowed to vote for three different snacks per calendar month.
    """
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,  # If a user is deleted, delete their votes, too.
        related_name='votes', help_text=_('User who placed the vote.')
    )
    snack_id = models.PositiveIntegerField(
        verbose_name=_('Snack ID'),
        help_text=_('ID of the snack being voted for.')
    )

    def __str__(self):
        tmpl = "{self.user.username} => {self.snack_id} on {self.created:%Y-%m-%d %H:%M:%S}"
        return tmpl.format(self=self)

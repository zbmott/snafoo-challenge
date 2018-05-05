# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.db import models
from django.utils import timezone


class SnacksDBBaseQuerySet(models.QuerySet):
    def this_month(self):
        beginning_of_the_month = timezone.now().replace(
            day=1, hour=0, minute=0,
            second=0, microsecond=0
        )

        return self.filter(created__gte=beginning_of_the_month)


class SnacksDBBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = SnacksDBBaseQuerySet.as_manager()

    class Meta:
        abstract = True

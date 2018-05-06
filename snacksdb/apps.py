from django.apps import AppConfig
from django.db.models.signals import post_save

from django.core.cache import cache


class SnacksDBConfig(AppConfig):
    name = 'snacksdb'

    def ready(self):
        post_save.connect(clear_cache, sender=self.get_model('Nomination'))


def clear_cache(sender, instance, created, **kw):
    """
    Each time we save a new Nomination, clear that user's monthly nomination
    count from the cache so that it can be recalculated.
    """
    if created:
        cache.delete(sender.get_monthly_nomination_cache_key(instance.user.pk))

# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.contrib import admin

from snacksdb.models import Ballot


class BallotAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'snack_id', 'created']
    list_filter = ['created']
    raw_id_fields = ['user']
    search_fields = ['user__username']

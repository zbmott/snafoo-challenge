# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.urls import include, path, re_path

from snacksdb import views

app_name = 'snacksdb'
urlpatterns = [
    re_path(r'^vote/?$', views.Vote.as_view(), name='vote'),
    re_path(r'^nominate/?$', views.Nominate.as_view(), name='nominate'),
]

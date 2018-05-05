# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'

from django.contrib import admin

from .NominationAdmin import Nomination, NominationAdmin
from .BallotAdmin import Ballot, BallotAdmin


models_to_register = [
    (Nomination, NominationAdmin),
    (Ballot, BallotAdmin),
]


for model, admin_class in models_to_register:
    admin.site.register(model, admin_class)

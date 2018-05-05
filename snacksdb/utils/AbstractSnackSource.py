# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'


class SnackSourceException(Exception):
    def __init__(self, msg):
        self.msg = msg


class AbstractSnackSource(object):
    def list(self):
        raise NotImplementedError()

    def suggest(self, name, location, latitude=None, longitude=None):
        raise NotImplementedError()

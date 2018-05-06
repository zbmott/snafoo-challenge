# vim: ts=4:sw=4:expandtabs

__author__ = 'zach.mott@gmail.com'


class SnackSourceException(Exception):
    def __init__(self, msg):
        self.msg = msg


class AbstractSnackSource(object):
    """
    Defines interface for pluggable snack sources.
    """
    def list(self):
        """
        Return a list of snacks that can be nominated or voted on. A snack is a
        dictionary that looks like this:
        {
            'id': int,
            'name': string,
            'optional': bool,
            'purchaseLocations': string,
            'purchaseCount': int,
            'lastPurchaseDate': string
        }

        Raise SnackSourceException if anything goes wrong.
        """
        raise NotImplementedError()

    def suggest(self, name, location, latitude=None, longitude=None):
        """
        Add a new snack. If successful, return a snack dictionary, as described in list().
        The new snack should be returned in future calls to list().

        Raise SnackSourceException if anything goes wrong.
        """
        raise NotImplementedError()

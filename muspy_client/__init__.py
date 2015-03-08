"""
OOP client for muspy.com
"""


__author__ = 'David Poisl <david@poisl.at>'
__version__ = '0.1.0'


from . import api


# TODO: docstrings
# TODO: nice representation
# TODO: testing


class ApiUser(object):
    """
    muspy.com user centric API

    :ivar str email: E-Mail Address
    :ivar str password: user password
    :ivar str userid: muspy.com user ID
    :ivar bool notify: notification per mail enabled
    :ivar bool notify_album: receive notifications for new albums
    :ivar bool notify_single: receive notifications for new singles
    :ivar bool notify_ep: receive notifications for new EPs
    :ivar bool notify_live: receive notifications for live albums
    :ivar bool notify_remix: receive notifications for remix releases
    :ivar bool notify_other: receive notifications for other stuff
    :ivar bool notify_compilation: receive notification for compilations
    """
    _fields = ('notify', 'notify_album', 'notify_single',
               'notify_ep', 'notify_live', 'notify_compilation',
               'notify_remix', 'notify_other', 'notify_compilation')

    @property
    def auth(self):
        """
        property for authentication data

        :return: tuple of (email/username, password)
        :rtype: tuple
        """
        return self.email, self.password

    def __init__(self, email, password):
        """
        constructor

        connects to the API and fetches user information.

        :param str email: email address for authentication
        :param str password: password
        """
        self.email = email
        self.password = password

        data = api.get_user(self.auth)
        assert(self.email == data.email)  # this should never happen
        self.userid = data.userid

        for key in self._fields:
            setattr(self, key, getattr(data, key))

        self._artists = ArtistList(self.auth, self.userid)

    @property
    def artists(self):
        """artists are read-only"""
        return self._artists

    @property
    def releases(self):
        """get all the releases"""
        for artist in self.artists:
            for release in artist.releases:
                yield release

    def __repr__(self):
        return "%s(email=%r, password='***')" % (self.__class__.__name__,
                                                 self.email)

    def __str__(self):
        return "<muspy.com UserInfo %r>" % self.userid

    @classmethod
    def register(cls, email, password, send_activation):  # TODO: untested
        api.create_user(email, password, send_activation)
        return cls(email, password)

    def delete(self):  # TODO: untested
        api.delete_user(self.auth, self.userid)

    def update(self):  # TOD: untested
        web_data = api.get_user(self.auth, self.userid)
        data = {k: getattr(self, k) for k in self._fields
                if getattr(self, k) != getattr(web_data, k)}
        return api.update_user(self.auth, self.userid, **data)


class ArtistList(object):
    """
    OOP abstraction for subscribed artist and management of subscribed artists

    this behaves more or less like a list.
    """
    def __init__(self, auth, userid):
        self._auth = auth
        self._userid = userid
        self._data = [Artist(a) for a in
                      api.list_artist_subscriptions(self._auth, self._userid)]

    def __repr__(self):
        return "ArtistList(%r)" % self._data

    def __str__(self):
        return "ArtistList(%s)" % self._data

    @staticmethod
    def _artist(other):
        if isinstance(other, api.ArtistInfo):
            return Artist(other)
        elif isinstance(other, basestring):
            return Artist(api.get_artist(other))
        else:
            raise ValueError("can't interpret %r" % other)

    def __iadd__(self, other):
        return self.add(other)

    def __isub__(self, other):
        return self.remove(other)

    def add(self, other):  # TODO: untested
        other = self._artist(other)
        if other in self._data:
            raise ValueError("%r already in list" % other)
        api.add_artist_subscription(self._auth, self._userid, other.mbid)
        return self._data.append(other)

    def remove(self, other):  # TODO: untested
        other = self._artist(other)
        if other not in self._data:
            raise ValueError("%r not in list" % other)
        api.remove_artist_subscription(self._auth, self._userid, other.mbid)
        self._data.remove(other)

    def __getitem__(self, item):
        return self._data.__getitem__(item)

    def __len__(self):
        return self._data.__len__()

    def __contains__(self, other):
        other = self._artist(other)
        return other in self._data

    def __iter__(self):
        return iter(self._data)

    iter = __iter__  # py2/py3 compatibility


class Artist(object):
    def __init__(self, artist):
        """
        constructor

        :param api.ArtistInfo artist: artist data
        """
        self._artist = artist
        self._releases = None

    @property
    def releases(self):
        if self._releases is None:
            self._releases = api.list_all_releases_for_artist(self._artist.mbid)
        return self._releases

    def __str__(self):
        return "<ArtistInfo %s>" % self._artist.name

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._artist)

    def __getattr__(self, name):
        return getattr(self._artist, name)

"""
client for muspy.com

a low level api can be found in the api submodule
"""


__author__ = 'David Poisl <david@poisl.at>'
__version__ = '0.1.0'


from . import api


class ApiUser(object):
    """
    muspy.com user centric API

    represents a user on muspy.com and his subscriptions.
    
    :ivar str email: E-Mail Address
    :ivar str password: user password
    :ivar str userid: muspy.com user ID
    :ivar ArtistList artists: subscribed artists

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

        connects to the API and fetches account information as well as
        the list of subscribed artists.

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
        """
        get the list of subscribed artists

        :return: list of subscribed artists
        :rtype: AristList
        """
        return self._artists

    @property
    def releases(self):
        """
        get all releases for subscribed artists

        Loads the artist list and all releases for these artists. This might 
        be a long-running operation, if you need this feature it might be 
        better to use the low-level functions in muspy_client.api
        """
        for artist in self.artists:
            for release in artist.releases:
                yield release

    def __repr__(self):
        return "%s(email=%r, password='***')" % (self.__class__.__name__,
                                                 self.email)

    def __str__(self):
        return "<muspy.com ApiUser %r>" % self.userid

    @classmethod
    def register(cls, email, password, send_activation=True):  # TODO: untested
        """
        register a new user

        if send_activation is set to False, the confirmation mail sent by 
        muspy.com to the given email address is not sent.

        :param str email: email address (=username)
        :param str password: password for the new account
        :param bool send_activation: send account confirmation mail
        :return: ApiUser instance for the new user
        :rtype: ApiUser
        """
        api.create_user(email, password, send_activation)
        return cls(email, password)

    def delete(self):  # TODO: untested
        """
        delete user from muspy.com

        This action can not be reversed. All user settings
        and the user is removed from muspy.com!
        
        :return: True on success
        :rtype: bool
        """
        api.delete_user(self.auth, self.userid)

    def update(self):  # TODO: untested
        """
        save user preferences

        after changing any of the writeable attributes (eG notifications)
        the data is not saved until update() is called.
        This is not needed for artist subscriptions, they are stored instantly.

        :return: updated user data
        :rtype: api.UserInfo
        """
        web_data = api.get_user(self.auth, self.userid)
        data = {k: getattr(self, k) for k in self._fields
                if getattr(self, k) != getattr(web_data, k)}
        return api.update_user(self.auth, self.userid, **data)


class ArtistList(object):
    """
    OOP abstraction for subscribed artist and management of subscribed artists

    this behaves more or less like a list where adding and removing items 
    subscribes or un-subscribes from the artist.
    """
    def __init__(self, auth, userid):
        """
        constructor

        Requires the authentication data and userid string of the user.

        :param tuple auth: authentication data (email, password)
        :param str userid: user id (must match auth data)
        """
        self._auth = auth
        self._userid = userid
        data = api.list_artist_subscriptions(self._auth, self._userid)
        self._data = [Artist.from_artist_info(a) for a in data]

    def __repr__(self):
        return "ArtistList(%r)" % self._data

    def __str__(self):
        return "ArtistList(%s)" % self._data

    @staticmethod
    def _artist(other):
        """
        helper to get an Artist instance

        takes an Artist, api.ArtistInfo or string to create
        an Artist instance. If a string is given, it is assumed
        to be a musicbrainz ID

        :param other: source object
        :type other: Artist|api.ArtistInfo|str
        :return: artist instance
        :rtype: Artist
        """
        if isinstance(other, api.ArtistInfo):
            return Artist.from_artist_info(other)
        elif isinstance(other, basestring):
            return Artist.from_artist_info(api.get_artist(other))
        else:
            raise ValueError("can't interpret %r" % other)
    
    def __iadd__(self, other):
        """subscribe to a new artist. see add(other)"""
        return self.add(other)

    def __isub__(self, other):
        """un-subscribe from an artist. see remove(other)"""
        return self.remove(other)

    def add(self, other):  # TODO: untested
        """
        subscribe to a new artist

        takes either an Artist or api.ArtistInfo instance or a string.
        Strings are assumed to be musicbrainz IDs for artists.

        :param other: artist to subscribe to
        :type other: Artist|api.ArtistInfo|str
        """
        other = self._artist(other)
        if other in self._data:
            raise ValueError("%r already in list" % other)
        api.add_artist_subscription(self._auth, self._userid, other.mbid)
        return self._data.append(other)

    def remove(self, other):  # TODO: untested
        """
        un-subscribe from an artist

        takes either an Artist or api.ArtistInfo instance or a string.
        Strings are assumed to be musicbrainz IDs for artists.

        :param other: artist to un-subscribe from
        :type other: Artist|api.ArtistInfo|str
        """
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
    """
    Artist Representation

    represents an artist as well as a list of all releases by
    this artist.

    :ivar str name: artist name
    :ivar str mbid: artist musicbrainz ID
    :ivar str sort_name: artist sort name (eG "Prodigy, The" for "The Prodigy")
    :ivar str disambiguation: a sort artist description if disambiguation 
                              is needed
    :ivar list releases: lazily loaded list of releases by this artist
    """
    def __init__(self, name, mbid, sort_name=None, disambiguation=""):
        """
        constructor

        :param str name: artist name
        :param str mbid: artist musicbrainz id
        :param str|None sort_name: sort name (if not set, set to artist)
        :param str|None disambiguation: disambiguation description if needed
        """
        self._releases = None
        self.name = name
        self.mbid = mbid
        self.sort_name = sort_name if sort_name is not None else name
        self.disambiguation = disambiguation
    
    @classmethod
    def from_artist_info(cls, artist_info):
        """
        create Artist from ArtistInfo instance

        :param api.ArtistInfo artist_info: ArtistInfo instance
        :return: Artist instance
        :rtype: Artist
        """
        return cls(artist_info.name, artist_info.mbid, artist_info.sort_name,
                   artist_info.disambiguation)

    @classmethod
    def from_mbid(cls, mbid):
        """
        load Artist from Musicbrainz ID

        :param str mbid: artist musicbrainz ID
        :return: Artist info
        :rtype: Artist
        """
        data = api.get_artist(mbid)
        return cls.from_artist_info(data)

    @property
    def releases(self):
        """
        list all releases of this artist

        this lazily fetches a list of all releases. Further reads are served
        from a cache and have no cost.
        The users preferences regarding which release types to notify for are
        respected here too.

        :return: list of artist releases
        :rtype: list(ReleaseInfo)
        """
        if self._releases is None:
            self._releases = api.list_all_releases_for_artist(self.mbid)
        return self._releases

    def __str__(self):
        return "<Artist %s>" % self.name

    def __repr__(self):
        return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.name,
                                       self.mbid, self.sort_name,
                                       self.disambiguation)

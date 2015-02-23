'''
client for muspy.com
'''

__author__ = 'David Poisl <david@poisl.at>'
__version__ = '1.0.0'


from . import api


class User(object):
    def __init__(self, email, userid, notify, **kwargs):
        self.email = email
        self.userid = userid
        self.notify = notify
        self.notifications = {k: v for (k, v) in kwargs.items() if k.startswith("notify_")}
        self._artists = None
        self._auth = kwargs.get("auth", None)
        
    def __repr__(self):
        return "%s(email=%r, userid=%r, notify=%r, auth=%r, **%r)" % (
                self.__class__.__name__, self.email, self.userid,
                self.notify, self._auth, self.notifications)
    
    def __str__(self):
        return "<User %s:%s>" % (self.email, self.userid)
    
    @classmethod
    def connect(cls, email, password):
        auth = (email, password)
        info = api.get_user_info(auth)
        return cls(auth=auth, **info)

    @property
    def artists(self):
        if self._artists is None:
            self._artists = [Artist(user=self, **x) for x in api.list_subscribed_artists(self._auth, self.userid)]
        return self._artists
 

class Artist(object):
    def __init__(self, user, name, sort_name, disambiguation, mbid):
        self._user = user
        self.name = name
        self.disambiguation = disambiguation
        self.sort_name = sort_name
        self.mbid  = mbid
        self._releases = None
    
    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r)" % (self.__class__.__name__, self._user, 
                self.name, self.sort_name, self.disambiguation, self.mbid)
    
    def __str__(self):
        return '<Artist:%r>' % self.sort_name
    
    @property
    def releases(self):
        if self._releases is None:
            data = api.get_releases(self._user._auth, self._user.userid, 
                                    self.mbid)
            self._releases = [Release(row, self) for row in data]
        return self._releases


class Release(object):
    def __init__(self, name, type, date, mbid, artist, _artist=None):
        self.name = name
        self.type = type
        self.date = date
        self.mbid = mbid
        self.artist = _artist if _artist else artist

    def __repr__(self):
        return "%s(%r, %r, %r, %r, %r)" % (self.__class__.__name__, self.name,
                self.type, self.date, self.mbid, self.artist)
    
    def __str__(self):
        return "<Release %r (%s)>" % (self.name, self.type)

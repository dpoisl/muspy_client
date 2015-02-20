'''
client for muspy.com
'''

__author__ = 'David Poisl <david@poisl.at>'
__version__ = '1.0.0'


import requests


class Client(object):
    '''
    client for the muspy.com API

    :cvar str _base_url: base URL for API calls
    :ivar requests.Session _session: request Session
    '''
    _base_url = 'https://muspy.com/api/1'

    def __init__(self, username=None, password=None):
        """
        constructor

        :param str username: username for API calls
        :param str password: password for API calls
        :return:
        """
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
        self._user_info = self.get_user_info()

    def _get(self, url, params=None):
        r = self.session.get(url, params=params)
        if r.status_code != requests.codes.ok:
            print(r.text)
            raise RuntimeError('Status code %r' % r.status_code)
        return r.json()

    def get_user_info(self, userid=None):
        url = '%s/user/%s' % (
            self._base_url,
            self._user_info["userid"] if userid is None else userid)
        return self._get(url)

    def list_artists(self, userid=None):
        url = '%s/artists/%s' % (
            self._base_url, userid if userid else self._user_info["userid"])
        return self._get(url)

    def add_artist(self, userid, artist_mbid):
        url = "%s/artists/%s/%s" % (self._base_url, userid, artist_mbid)
        r = self.session.put(url)
        if r.status_code != requests.codes.ok:
            print(r.text)
            raise RuntimeError('Status code %r' % r.status_code)
        return r.json()  # TODO: do we get json here? if yes, what?

    def remove_artist(self, userid, artist_mbid):
        url = "%s/artists/%s/%s" % (self._base_url, userid, artist_mbid)
        r = self.session.delete(url)
        if r.status_code != requests.codes.ok:
            print(r.text)
            raise RuntimeError('Status code %r' % r.status_code)
        return r.json()  # TODO: do we get json here? if yes, what?


    def get_releases(self, limit=100, offset=0, artist_mbid=None):
        params = {'limit': limit, 'offset': offset}
        if artist_mbid:
            params['mbid'] = artist_mbid
        url = '%s/releases/%s' % (self._base_url, self._user_info["userid"])
        return self._get(url, params)

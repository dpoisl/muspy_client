"""
low level api access to muspy.com

implementation of all API endpoints described at
https://github.com/alexkay/muspy/tree/master/api/
"""


__author__ = 'David Poisl <david@poisl.at>'
__version__ = '0.1.0'


import requests
import collections


RELEASE_LIST_LIMIT = 100  # maximum number of releases per request
LASTFM_IMPORT_LIMIT = 500  # maximum artists to import from last.fm
API_BASE_URL = 'https://muspy.com/api/1'  # base url for API calls


ArtistInfo = collections.namedtuple('ArtistInfo', ('name', 'mbid', 'sort_name',
                                                   'disambiguation'))


ReleaseInfo = collections.namedtuple('ReleaseInfo', ('name', 'mbid', 'date',
                                                     'type', 'artist'))


UserInfo = collections.namedtuple('UserInfo', ('userid', 'email', 'notify',
                                               'notify_album', 'notify_single',
                                               'notify_ep', 'notify_live',
                                               'notify_compilation',
                                               'notify_remix', 'notify_other'))


def _release_from_json(json_response):
    """
    convert release info from json format to ReleaseInfo

    converts he sub-dict for artist to an ArtistInfo too

    :param dict json_response: JSON data for an release
    :return: parsed and converted release info
    :rtype: ReleaseInfo
    """
    artist = ArtistInfo(**json_response['artist'])
    data = json_response.copy()
    data['artist'] = artist
    return ReleaseInfo(**data)


def get_artist(mbid):
    """
    get information about an artist

    :param str mbid: musicbrainz id of the artist to query
    :return: fetched ArtistInfo
    :rtype: ArtistInfo
    :raises: HTTPError 410 if the artist mbid is not found
    :raises: HTTPError 404 if the artist mbid is syntactically invalid
    """
    url = '%s/artist/%s' % (API_BASE_URL, mbid)
    response = requests.get(url)
    response.raise_for_status()
    return ArtistInfo(**response.json())


def list_artist_subscriptions(auth, userid):
    """
    list all artists a user subscribed to

    :param tuple auth: authentication data (username, password)
    :param str userid: user id (must match auth data)
    :return: subscribed artists
    :rtype: list(ArtistInfo)
    :raises: HTTPError 401 if auth failed or the userid doesn't match
    :raises: HTTPError 404 if the userid is syntactically invalid
    :raises:
    """
    url = '%s/artists/%s' % (API_BASE_URL, userid)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return [ArtistInfo(**row) for row in response.json()]


def add_artist_subscription(auth, userid, artist_mbid):
    """
    add an artist to the list of subscribed artists

    :param tuple auth: authentication data (username, password)
    :param str userid: user ID (must match auth data)
    :param str artist_mbid: musicbrainz ID of the artist to add
    :return: True on success
    :raises: HTTPError 401 if auth failed or the userid doesn't match
    :raises: HTTPError 404 if the userid or artist_mbid is syntactically invalid
    """
    url = '%s/artists/%s/%s' % (API_BASE_URL, userid, artist_mbid)
    response = requests.put(url, auth=auth)
    response.raise_for_status()
    return True


def import_lastfm_subscriptions(auth, userid, lastfm_username,
                                limit=LASTFM_IMPORT_LIMIT,
                                period='overall'):  # TODO: testing
    """
    import last.fm artists to a user

    :param tuple auth: authentication data (username, password)
    :param str userid: user ID (must match auth data)
    :param str lastfm_username: last.fm lastfm_username
    :param int limit: number of artists to import
    :param str period: period to examine. one of 'overall', '12month',
                      '6month', '3month' or '7day'
    :return: True on success
    """
    url = '%s/artists/%s' % (API_BASE_URL, userid)
    if period not in ('overall', '12month', '6month', '3month', '7day'):
        raise ValueError('invalid period: %r' % period)
    if limit < 0 or limit > LASTFM_IMPORT_LIMIT:
        raise ValueError('invalid limit: %r' % limit)

    response = requests.put(url, auth=auth,
                            data={'lastfm_username': lastfm_username,
                                  'count': limit, 'period': period})
    response.raise_for_status()
    return True


def remove_artist_subscription(auth, userid, artist_mbid):
    """
    remove an artist from the list of subscribed artists

    :param tuple auth: tuple containint (username, password)
    :param str userid: user ID (must match auth data)
    :param artist_mbid: musicbrainzid of the artist to remove
    :return: True on success
    :raises: HTTPError 401 if auth failed or the userid doesn't match
    :raises: HTTPError 404 if the userid or artist_mbid is syntactically invalid
    """
    url = '%s/artists/%s/%s' % (API_BASE_URL, userid, artist_mbid)
    response = requests.delete(url, auth=auth)
    response.raise_for_status()
    return True


def get_release(release_mbid):
    """
    get information about a release

    :param str release_mbid: musicbrainz id of the release to query
    :return: the release data
    :rtype: ReleaseInfo
    """
    url = '%s/release/%s' % (API_BASE_URL, release_mbid)
    response = requests.get(url)
    response.raise_for_status()
    json = response.json()
    json['artist'] = ArtistInfo(**json['artist'])
    return ReleaseInfo(json)


def list_all_releases_for_artist(artist_mbid, userid=None):
    """
    get all releases for a given artist.

    returns all releases for one artist. If the userid is set, the users
    filters regarding release types to report are respected.
    This calls list_releases in a loop with the maximum allowed limit.

    :param str artist_mbid: musicbrainz id for the artist
    :param str|None userid: user id for filter rules
    :return: list of releases matching user filter and artist mbid
    :rtype: list(ReleaseInfo)
    :raises: HTTPError 404 if a parameter is syntactically invalid
    """
    limit = RELEASE_LIST_LIMIT
    offset = 0
    result = []
    while True:
        part = list_releases(userid=userid, artist_mbid=artist_mbid,
                             limit=limit, offset=offset)
        result += part
        if len(part) < RELEASE_LIST_LIMIT:
            return result
        offset += len(part)


def list_releases(userid=None, artist_mbid=None, limit=None, offset=None,
                 since=None):
    """
    get releases for an artist (or all releases)

    various filters can be applied. if a userid is given, the users
    preferences regarding release types to show are respected.
    The optional limit controls the maximum number of releases returned and
    the offset controls the first record to return. If since is set to a
    release artist_mbid, all releases after this release are returned.

    :param str|None userid: user id to take release types from
    :param int|None limit: limit records per response
    :param int|None offset: offset for first returned record
    :param str|None artist_mbid: artist artist_mbid
    :param str|None since: search releases after that release
    :return: list of releases matchin gthe given criteria
    :rtype: list(ReleaseInfo)
    :raises: HTTPError 404 if a parameter is syntactically invalid
    """
    if userid is None:
        url = '%s/releases' % API_BASE_URL
    else:
        url = '%s/releases/%s' % (API_BASE_URL, userid)

    params = {}
    if limit is not None:
        if limit < 0 or limit > RELEASE_LIST_LIMIT:
            raise ValueError('limit %r is invalid' % limit)
        params['limit'] = limit
    if offset is not None:
        params['offset'] = offset
    if artist_mbid is not None:
        params['mbid'] = artist_mbid
    if since is not None:
        params['since'] = since

    response = requests.get(url, params=params)
    response.raise_for_status()
    return [_release_from_json(row) for row in response.json()]


def get_user(auth, userid=None):
    """
    get info for a user - requires authentication

    if no userid is given, the user matching the authentication info is returned

    :param tuple auth: (username, password)
    :param str|None userid: user to query
    :return: user instanct
    :rtype: UserInfo
    :raises HTTPError 400 if the userid doesn't match authentication data
    :raises HTTPError 401 if the authentication failed
    """
    if userid is None:
        url = '%s/user' % (API_BASE_URL,)
    else:
        url = '%s/user/%s' % (API_BASE_URL, userid)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return UserInfo(**response.json())


def create_user(email, password, send_activation=True):  # TODO: testing
    """
    register a new user

    :param str email: email address for the new user (=username)
    :param str password: password for the new user
    :param bool send_activation:
    :return:
    :raises: HTTPError
    """
    url = '%s/user' % (API_BASE_URL,)
    response = requests.post(url, data={'email': email, 'password': password,
                                        'activate': int(send_activation)})
    response.raise_for_status()
    return True


def delete_user(auth, userid):  # TODO: testing
    """
    delete a user

    this does NOT ask for confirmation

    :param tuple auth: authentication data (username, password)
    :param userid: user id to delete (must match auth data)
    :return: True on success
    """
    url = '%s/user/%s' % (API_BASE_URL, userid)
    response = requests.delete(url, auth=auth)
    response.raise_for_status()
    return True


def update_user(auth, userid, **kwargs):
    """
    update user profile

    updates user settings. if settings are omitted from kwargs, they are
    kept. Valid settings and their type are:
      * email: string, email address (requires new confirmation)
      * notify: bool, notifications per E-Mail
      * notify_album: bool, notify on new albums
      * notify_single: bool, notify on new singles
      * notify_ep: bool, notify on new EPs
      * notify_live: bool, notify on new live shows
      * notify_compilation: bool, notify on new compilations
      * notify_remix: bool, notify on new remixes
      * notify_other: bool, notify on other releases

    :param tuple auth: authentication data (username, password)
    :param str userid: user id to modify (must match auth data)
    :param dict kwargs: user settings to modify.
    :return: the new user settings
    :rtype: UserInfo
    """
    data = {}
    for (key, value) in kwargs.items():
        if key in ('notify', 'notify_album', 'notify_single', 'notify_ep',
                   'notify_live', 'notify_compilation', 'notify_remix',
                   'notify_other'):
            data[key] = 1 if value else 0
        elif key in ('email',):
            data[key] = value
        else:
            raise RuntimeError('invalid argument: %r' % key)

    url = '%s/user/%s' % (API_BASE_URL, userid)
    response = requests.put(url, auth=auth, data=data)
    response.raise_for_status()
    return UserInfo(**response.json())

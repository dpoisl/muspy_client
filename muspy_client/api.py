"""
low level api access to muspy.com

implements all API endpoints defined in the documentation found at
https://github.com/alexkay/muspy/tree/master/api/ at a low level.
"""


__author__ = 'David Poisl <david@poisl.at>'
__version__ = '1.0.0'


import requests


RELEASE_LIST_LIMIT = 100  # maximum number of releases per request
LASTFM_IMPORT_LIMIT = 500  # maximum artists to import from last.fm
API_BASE_URL = 'https://muspy.com/api/1'  # base url for API calls


def get_artist(mbid):  # TODO: testing
    """
    get information about an artist

    :param str mbid: musicbrainz id of the artist to query
    :return: dictionary with artist data
    :rtype: dict
    """
    url = "%s/artist/%s" % (API_BASE_URL, mbid)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def list_subscribed_artists(auth, userid):
    """
    list all artists a user subscribed to

    :param tuple auth: authentication data (username, password)
    :param str userid: user id (must match auth data)
    :return: subscribed artists
    :rtype: list
    """
    url = '%s/artists/%s' % (API_BASE_URL, userid)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()


def subscribe_to_artist(auth, userid, mbid):  # TODO: testing
    """
    add an artist to the list of subscribed artists

    :param tuple auth: authentication data (username, password)
    :param str userid: user ID (must match auth data)
    :param str mbid: musicbrainz ID of the artist to add
    :return: True on success
    """
    url = "%s/artists/%s/%s" % (API_BASE_URL, userid, mbid)
    response = requests.put(url, auth=auth)
    response.raise_for_status()
    return True


def import_lastfm_artists(auth, userid, username, count=LASTFM_IMPORT_LIMIT,
                          period='overall'):  # TODO: testing
    """
    import last.fm artists to a user

    :param tuple auth: authentication data (username, password)
    :param str userid: user ID (must match auth data)
    :param str username: last.fm username
    :param int count: number of artists to import
    :param str period: period to examine. one of 'overall', '12month',
                      '6month', '3month' or '7day'
    :return: True on success
    """
    url = "%s/artists/%s" % (API_BASE_URL, userid)
    if period not in ('overall', '12month', '6month', '3month', '7day'):
        raise ValueError("invalid period: %r" % period)
    if count < 0 or count > LASTFM_IMPORT_LIMIT:
        raise ValueError("invalid count: %r" % count)

    response = requests.put(url, auth=auth, data={"username": username,
                                                  "count": count,
                                                  "period": period})
    response.raise_for_status()
    return True


def unsubscribe_from_artist(auth, userid, mbid):  # TODO: testing
    """
    remove an artist from the list of subscribed artists

    :param tuple auth: tuple containint (username, password)
    :param str userid: user ID (must match auth data)
    :param mbid: musicbrainzid of the artist to remove
    :return: True on success
    """
    url = "%s/artists/%s/%s" % (API_BASE_URL, userid, mbid)
    response = requests.delete(url, auth=auth)
    response.raise_for_status()
    return True


def get_release(mbid):  # TODO: testing
    """
    get information about a release

    :param str mbid: musicbrainz id of the release to query
    :return: dictionary with release data (artist, mbid, name, type, date)
    :rtype: dict
    """
    url = "%s/release/%s" % (API_BASE_URL, mbid)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_all_releases_for_artist(mbid, userid=None):  # TODO: testing
    """
    get all releases for a given artist.

    returns all releases for one artist. If the userid is set, the users
    filters regarding release types to report are respected.
    This calls get_releases in a loop with the maximum allowed limit.

    :param str mbid: musicbrainz id for the artist
    :param str|None userid: user id for filter rules
    :return: list of releases
    :rtype: list
    """
    limit = RELEASE_LIST_LIMIT
    offset = 0
    result = []
    while True:
        part = get_releases(userid=userid, mbid=mbid, limit=limit,
                            offset=offset)
        result += part
        if len(part) < RELEASE_LIST_LIMIT:
            return result
        offset += len(part)


def get_releases(userid=None, limit=None, offset=None, mbid=None,
                 since=None):  # TODO: testing
    """
    get releases for an artist (or all releases)

    various filters can be applied. if a userid is given, the users
    preferences regarding release types to show are respected.
    The optional limit controls the maximum number of releases returned and
    the offset controls the first record to return. If since is set to a
    release mbid, all releases after this release are returned.

    :param str|None userid: user id to take release types from
    :param int|None limit: limit records per response
    :param int|None offset: offset for first returned record
    :param str|None mbid: artist mbid
    :param str|None since: search releases after that release
    :return: list of releases
    :rtype: list
    """
    if userid is None:
        url = "%s/releases" % API_BASE_URL
    else:
        url = "%s/releases/%s" % (API_BASE_URL, userid)

    params = {}
    if limit is not None:
        if limit < 0 or limit > RELEASE_LIST_LIMIT:
            raise ValueError("limit %r is invalid" % limit)
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    if mbid is not None:
        params["mbid"] = mbid
    if since is not None:
        params["since"] = since

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_user(auth, userid=None):
    """
    get info for a user - requires authentication

    if no userid is given, the user matching the authentication info is returned

    :param tuple auth: (username, password)
    :param str|None userid: user to query
    :return:
    """
    if userid is None:
        url = '%s/user' % (API_BASE_URL,)
    else:
        url = "%s/user/%s" % (API_BASE_URL, userid)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()


def create_user(email, password, send_activation=True):  # TODO: untested
    """
    register a new user

    :param str email: email address for the new user (=username)
    :param str password: password for the new user
    :param bool send_activation:
    :return:
    """
    url = '%s/user' % (API_BASE_URL,)
    response = requests.post(url,
                             data={"email": email, "password": password,
                                   "activate": 1 if send_activation else 0})
    response.raise_for_status()
    return response.json()  # TODO: JSON?


def delete_user(auth, userid):  # TODO: testing
    """
    delete a user

    this does NOT ask for confirmation!

    :param tuple auth: authentication data (username, password)
    :param userid: user id to delete (must match auth data)
    :return: True on success
    """
    url = "%s/user/%s" % (API_BASE_URL, userid)
    response = requests.delete(url, auth=auth)
    response.raise_for_status()
    return True


def update_user(auth, userid, **kwargs):  # TODO: testing
    """
    update user profile

    updates user settings. if settings are ommited from kwargs, they are
    kept. Valid settings and teir type are:
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
    :rtype: dict
    """
    data = {}
    for (key, value) in kwargs.items():
        if key in ("notify", "notify_album", "notify_single", "notify_ep",
                   "notify_live", "notify_compilation", "notify_remix",
                   "notify_other"):
            data[key] = 1 if value else 0
        elif key in ("email",):
            data[key] = value
        else:
            raise RuntimeError("invalid argument: %r" % key)

    url = "%s/user/%s" % (API_BASE_URL, userid)
    response = requests.put(url, auth=auth, data=data)
    response.raise_for_status()
    return response.json()

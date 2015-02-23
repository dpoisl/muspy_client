'''
client for muspy.com
'''

__author__ = 'David Poisl <david@poisl.at>'
__version__ = '1.0.0'


import requests


RELEASE_LIST_LIMIT = 100
API_BASE_URL = 'https://muspy.com/api/1'


def get_user_info(auth, userid=None):
    url = '%s/user' % (API_BASE_URL)
    if userid is not None:
        url = url + "/%s" % userid
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()


def list_subscribed_artists(auth, userid):
    url = '%s/artists/%s' % (API_BASE_URL, userid)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()


def subscribe_to_artist(auth, userid, mbid):
    url = "%s/artists/%s/%s" % (API_BASE_URL, userid, mbid)
    response = requests.put(url, auth=auth)
    response.raise_for_status()
    return True


def unsubscribe_from_artist(auth, userid, mbid):
    url = "%s/artists/%s/%s" % (API_BASE_URL, userid, mbid)
    response = requests.delete(url, auth=auth)
    response.raise_for_status()
    return True


def get_releases(auth, userid=None, mbid=None):
    url = "%s/releases" % API_BASE_URL
    if userid is not None:
        url = url + "/%s" % userid
    
    params = {"limit": RELEASE_LIST_LIMIT, "offset": 0}
    if mbid is not None:
        params["mbid"] = mbid
    
    result = []
    while True:
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()
        part = response.json()
        result += part
        if len(part) < 100:
            return result


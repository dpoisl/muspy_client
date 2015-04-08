Low-Level API
=============

The low level API provides a direct access to the functions provided by the
web API.

Authentication is required for some API calls, in these cases he
authentication must be a tuple containing the e-mail address and password of
a registered user. If a call also requires the user ID it must match the
authentication information.

Result Classes
--------------

Results from API calls are always :class:`collections.namedtuple` instances.

 * Artists are :class:`muspy_client.api.ArtistInfo` instances
 * Releases are :class:`muspy_client.api.ReleaseInfo` instances. The
   attribute artist here is another :class:`~muspy_client.api.ArtistInfo`
   instance
 * Users are :class:`muspy_client.api.UserInfo` instances



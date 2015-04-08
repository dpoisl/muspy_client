Object-Oriented API
===================

This section gives a brief overview of the OOP API. For details look at the
:doc:`api`.

An User-Based Approach
----------------------

By creating an :class:`muspy_client.ApiUser` instance the user preferences
as well as the subscribed artists are prefetched. By setting the attributes
of the user instance and then calling
:meth:`~muspy_client.ApiUser.update` the settings are stored on the server.

Artist Subscriptions
--------------------

The :attr:`~muspy_client.ApiUser.artists` property is a
:class:`~muspy_client.ArtistList` instance which behaves like an
iterable containing :class:`~muspy_client.Artist` instances.

Its :meth:`~muspy_client.ArtistList.add` method subscribes
to a new artist and can be called with an Artist instance or with the mbid of
an artist. The :meth:`~muspy_client.ArtistList.remove` method removes an
artist from the users subscriptions. Unlike changing the users preferences,
these operations are always executed without delay.

Getting Releases
----------------

Each artist has an :attr:`~muspy_client.Artist.releases` property. This
attribute shows all releases that match the users filters defined in the
notify_* attributes. If eG the user has notify_ep set to False not EPs will
be shown in the release list for his artists.

Releases are fetched when the attribute is accessed the first time, after
that only the cached data is returned to avoid unnessecary API calls.

The :class:`muspy_client.ApiUser` attribute
:meth:`~muspy_client.ApiUser.releasees` shows the releases for all artists
the user has subscribed. This fetches the release list for each artist which
can take some time on larger subscription lists or artists with many releases.

Registering a new User
----------------------

The :meth:`muspy_client.ApiUser.register` classmethod takes care of
registering a new account. A confirmation mail is sent and the user must be
activated before it can be used to query the API.

Deleting a User
---------------

It is possible to delete a user via the API by calling
:meth:`~muspy_client.ApiUser.delete`. This will not ask for confirmation and
will delete the users settings, subscriptions and the account itself.

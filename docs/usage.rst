General Constraints
===================

Authentication and Users
------------------------

Authentication is required for some API calls. The credentials are usually
the e-mail address of an account and the corresponding password. Although
some API calls take a user id in their parameters this user id must be of the
same user as the authentication credentials.

Musicbbrainz.org IDs
--------------------

Artists and Releases are identified by their id from http://musicbrainz.org in
all API calls -- called **mbid** for short. Fetching the mbid for an artist
or release is out of scope for this project but pypi contains a few libraries
to talk to musicbrainz.

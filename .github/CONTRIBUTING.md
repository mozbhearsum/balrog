# Contributing to Balrog

In order to effectively work on Balrog you will need to be able to both run its tests and local development environment. You will need a recent version of Docker, Docker Compose, and tox to do these things.

## Running tests

To run Balrog's unit tests, run `tox`. This will run the unit tests in a local Docker image.

## Running the apps

To run Balrog's local development environment, run `docker-compose up`. It will take some time to build the necessary containers the first time you do this. Once they've successfully built, you should be able to access the following URLs:
* https://localhost:9010 - The public API
* https://localhost:8010 - The admin API
* http://localhost:9000 - The admin interface

You will need to accept the self signed certificate presented for the public and admin APIs in order for everything to work correctly.

You will also need to sign in to the admin interface to do anything useful there. It will ask you to sign in with a third party provider (eg: gmail, github). Once you've done that, run the following to create a local admin user to gain write access:

```bash
    $ export LOCAL_ADMIN=<email address you signed in with>
    $ docker-compose run balrogadmin create-local-admin
```

## Finding bugs to work on

If you're new to Balrog, it is recommended that you find a [Good First Bug](https://github.com/mozilla-releng/balrog/issues?q=is%3Aissue+is%3Aopen+label%3Afirst-bug) to look at as a starting point. Otherwise, the [Admin](https://github.com/mozilla-releng/balrog/labels/admin), [Agent](https://github.com/mozilla-releng/balrog/labels/agent), [Public](https://github.com/mozilla-releng/balrog/labels/public), and [DB](https://github.com/mozilla-releng/balrog/labels/db) labels cover most of the open backend issues (written in Python), while the [UI](https://github.com/mozilla-releng/balrog/labels/ui) label covers the frontend issues (written in React).

# More information

More information about Balrog can be found in [the documentation](http://mozilla-balrog.readthedocs.io/en/latest/index.html).

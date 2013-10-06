#!/usr/bin/env python

''' py.test configuration and fixtures file.

Tells application she's running in a test environment.
Creates a complete web2py environment, similar to web2py shell.
Creates a WebClient instance to browse your application, similar to a real
web browser.
Propagates some application data to test cases via fixtures, like baseurl and
automatic appname discovering.
'''

import os
import pytest
import sys

sys.path.insert(0, '')

@pytest.fixture(scope='session')
def baseurl(appname):
    '''The base url to call your application.

    Change you port number as necessary.
    '''

    return 'http://localhost:8000/%s' % appname


@pytest.fixture(scope='session')
def appname():
    '''Discover application name.

    Your test scripts must be on applications/<your_app>/tests
    '''

    dirs = os.path.split(__file__)[0]
    appname = dirs.split(os.path.sep)[-2]
    return appname


@pytest.fixture(scope='session', autouse=True)
def fixture_create_testfile_to_application(request, appname):
    '''Creates a temp file to tell application she's running under a
    test environment.

    Usually you will want to create your database in memory to speed up
    your tests and not change your development database.

    This fixture is automatically run by py.test at session level. So, there's
    no overhad to test performance.
    '''

    from ..modules.web2pytest import web2pytest
    web2pytest.create_testfile(appname)

    request.addfinalizer(web2pytest.delete_testfile)


@pytest.fixture(autouse=True)
def fixture_cleanup_db(web2py):
    '''Truncate all database tables before every single test case.

    This can really slow down your tests. So, keep your test data small and try
    to allocate your database in memory.

    Automatically called by test.py due to decorator.
    '''

    web2py.db.rollback()
    for tab in web2py.db.tables:
        web2py.db[tab].truncate()
    web2py.db.commit()


@pytest.fixture(scope='session')
def client(baseurl):
    '''Create a new WebClient instance once per session.
    '''

    from gluon.contrib.webclient import WebClient
    webclient = WebClient(baseurl)
    return webclient


@pytest.fixture()
def web2py(appname):
    '''Create a Web2py environment similar to that achieved by
    Web2py shell.

    It allows you to use global Web2py objects like db, request, response,
    session, etc.

    Concerning tests, it is usually used to check if your database is an
    expected state, avoiding creating controllers and functions to help
    tests.
    '''

    from gluon.shell import env
    from gluon.storage import Storage

    web2py_env = env(appname, import_models=True,
                     extra_request=dict(is_local=True,
                                        _running_under_test=True))

    del web2py_env['__file__']  # avoid py.test import error
    globals().update(web2py_env)

    return Storage(web2py_env)

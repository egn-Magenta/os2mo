# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import json
import logging
import pprint
from time import sleep
from unittest.case import TestCase

import requests
from aiohttp import ClientOSError
from starlette.testclient import TestClient

from mora import app, conf_db, service, settings
from mora.async_util import _local_cache, async_to_sync
from mora.auth.keycloak.oidc import auth
from mora.request_scoped.bulking import request_wide_bulk
from tests.util import _mox_testing_api, load_sample_structures

logger = logging.getLogger(__name__)


async def fake_auth():
    return {
        'acr': '1',
        'allowed-origins': ['http://localhost:5001'],
        'azp': 'vue',
        'email': 'bruce@kung.fu',
        'email_verified': False,
        'exp': 1621779689,
        'family_name': 'Lee',
        'given_name': 'Bruce',
        'iat': 1621779389,
        'iss': 'http://localhost:8081/auth/realms/mo',
        'jti': '25dbb58d-b3cb-4880-8b51-8b92ada4528a',
        'name': 'Bruce Lee',
        'preferred_username': 'bruce',
        'scope': 'email profile',
        'session_state': 'd94f8dc3-d930-49b3-a9dd-9cdc1893b86a',
        'sub': 'c420894f-36ba-4cd5-b4f8-1b24bd8c53db',
        'typ': 'Bearer'
    }


class _BaseTestCase(TestCase):
    """
    Base class for MO testcases w/o LoRA access.
    """

    maxDiff = None

    def setUp(self):
        super().setUp()
        self.app = self.create_app()
        self.client = TestClient(self.app)

        # Bypass Keycloak per default
        self.app.dependency_overrides[auth] = fake_auth

    def create_app(self, overrides=None):
        # make sure the configured organisation is always reset
        # every before test
        service.org.ConfiguredOrganisation.valid = False
        app_ = app.create_app()

        return app_

    @property
    def lora_url(self):
        return settings.LORA_URL

    def get_token(self):
        """
        Get OIDC token from Keycloak to send with the request
        to the MO backend.
        """
        r = requests.post(
            'http://keycloak:8080'
            '/auth/realms/mo/protocol/openid-connect/token',
            data={
                'grant_type': 'password',
                'client_id': 'mo',
                'username': 'bruce',
                'password': 'bruce'
            }
        )
        return r.json()['access_token']

    def assertRequest(self, path, status_code=None, message=None, *,
                      drop_keys=(), amqp_topics=(), set_auth_header=False,
                      **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        :return: The result of the request, as a string or object, if
                 JSON.

        '''

        # Get OIDC token from Keycloak and add an auth request header
        if set_auth_header:
            kwargs.setdefault('headers', dict()).update(
                {'Authorization': 'bearer ' + self.get_token()}
            )

        r = self.request(path, **kwargs)

        if r.headers.get('content-type') == 'application/json':
            actual = r.json()
        else:
            print(r.headers, r.content, r.raw)
            actual = r.text

        # actual = (
        #     json.loads(r.get_data(True))
        #     if r.mimetype == 'application/json'
        #     else r.get_data(True)
        # )

        if status_code is None:
            if message is None:
                message = 'status of {!r} was {}, not 2xx'.format(
                    path,
                    r.status_code,
                )

            if not 200 <= r.status_code < 300:
                pprint.pprint(actual)

                self.fail(message)

        else:
            if message is None:
                message = 'status of {!r} was {}, not {}'.format(
                    path,
                    r.status_code,
                    status_code,
                )

            if r.status_code != status_code:
                ppa = pprint.pformat(actual)
                print(f'actual response:\n{ppa}')

                self.fail(message)

        for k in drop_keys:
            try:
                actual.pop(k)
            except (IndexError, KeyError, TypeError):
                pass

        return actual

    def assertRequestResponse(self, path, expected, message=None,
                              amqp_topics=(), set_auth_header=False, **kwargs):
        '''Issue a request and assert that it succeeds (and does not
        redirect) and yields the expected output.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        '''

        actual = self.assertRequest(path, message=message,
                                    amqp_topics=amqp_topics,
                                    set_auth_header=set_auth_header,
                                    **kwargs)

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        self.assertEqual(expected, actual, message)

    def assertRequestFails(self, path, code, message=None,
                           set_auth_header=False, **kwargs):
        '''Issue a request and assert that it fails with the given status.

        ``**kwargs`` is passed directly to the test client -- see the
        documentation for :py:class:`werkzeug.test.EnvironBuilder` for
        details.

        One addition is that we support a ``json`` argument that
        automatically posts the given JSON data.

        '''

        self.assertRequest(path, message=message, status_code=code,
                           set_auth_header=set_auth_header, **kwargs)

    def request(self, path, **kwargs):
        if 'json' in kwargs:
            # "In the face of ambiguity, refuse the temptation to guess."
            # ...so check that the arguments we override don't exist
            assert kwargs.keys().isdisjoint({'method', 'data'})

            # kwargs['method'] = 'POST'
            kwargs['data'] = json.dumps(kwargs.pop('json'), indent=2)
            kwargs.setdefault('headers', dict()).update(
                {'Content-Type': 'application/json'}
            )
            return self.client.post(path, **kwargs)

        return self.client.get(path, **kwargs)

    @staticmethod
    def __sort_inner_lists(obj):
        """Sort all inner lists and tuples by their JSON string value,
        recursively. This is quite stupid and slow, but works!

        This is purely to help comparison tests, as we don't care
        about the list ordering

        """
        if isinstance(obj, dict):
            return {
                k: TestCase.__sort_inner_lists(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, (list, tuple)):
            return sorted(
                map(TestCase.__sort_inner_lists, obj),
                key=(lambda p: json.dumps(p, sort_keys=True)),
            )
        else:
            return obj

    def assertRegistrationsEqual(self, expected, actual, message=None):

        # drop lora-generated timestamps & users
        for k in 'fratidspunkt', 'tiltidspunkt', 'brugerref':
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        if actual != expected:
            pprint.pprint(actual)

        # Sort all inner lists and compare
        return self.assertEqual(expected, actual, message)

    def assertRegistrationsNotEqual(self, expected, actual, message=None):
        # drop lora-generated timestamps & users
        for k in 'fratidspunkt', 'tiltidspunkt', 'brugerref':
            expected.pop(k, None)
            actual.pop(k, None)

        actual = self.__sort_inner_lists(actual)
        expected = self.__sort_inner_lists(expected)

        # Sort all inner lists and compare
        return self.assertNotEqual(expected, actual, message)

    def assertSortedEqual(self, expected, actual, message=None):
        """Sort all inner-lists before comparison"""

        expected = self.__sort_inner_lists(expected)
        actual = self.__sort_inner_lists(actual)

        return self.assertEqual(expected, actual, message)


class TestCase(_BaseTestCase):
    pass


class LoRATestCase(_BaseTestCase):
    '''Base class for LoRA testcases; the test creates an empty LoRA
    instance, and deletes all objects between runs.
    '''

    def load_sample_structures(self, minimal=False):
        func = async_to_sync(load_sample_structures)
        for _ in range(5):
            try:
                return func(minimal)
            except ClientOSError:
                sleep(0.2)
                logging.exception("retrying")
        raise Exception("unable to complete")

    @classmethod
    def setUpClass(cls):
        _mox_testing_api("db-setup")
        request_wide_bulk._disable_caching()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        _mox_testing_api("db-teardown")
        super().tearDownClass()

    def setUp(self):
        _mox_testing_api("db-reset")
        super().setUp()

    @async_to_sync
    async def tearDown(self):
        if (
            hasattr(_local_cache, "async_session") and
            _local_cache.async_session is not None
        ):
            await _local_cache.async_session.close()
            _local_cache.async_session = None
        super().tearDown()


class ConfigTestCase(LoRATestCase):
    """Testcase with configuration database support."""

    def set_global_conf(self, conf):
        conf_db.set_configuration({'org_units': dict(conf)})

    @classmethod
    def setUpClass(cls):
        conf_db.config["configuration"]["database"]["name"] = "test_confdb"
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        conf_db._createdb(force=False)
        super().setUp()

    def tearDown(self):
        conf_db.drop_db()
        super().tearDown()

# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import unittest

import fastapi.routing
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK
)

from mora import main
from mora.auth.keycloak.oidc import auth
import tests.cases


class TestServiceAuth(unittest.TestCase):
    """
    Test that OIDC auth is enabled on all endpoints except from those
    specified in an explicit exclude list (see the NO_AUTH_ENDPOINTS below)
    """

    # No fancy logic (for security reasons) to set the excluded endpoints -
    # all excluded endpoints must be explicitly specified in the list

    NO_AUTH_ENDPOINTS = (
        '/health/amqp',
        '/health/oio_rest',
        '/health/configuration_database',
        '/health/dataset',
        '/health/dar',
        '/health/',
        '/version/',
        '/forespoergsler/',
        '/organisationssammenkobling/',
        '/medarbejder/{path:path}',
        '/medarbejder/',
        '/organisation/{path:path}',
        '/organisation/',
        '/',
        '/favicon.ico',
        '/service/keycloak.json',
        '/service/{rest_of_path:path}',
        '/testing/testcafe-db-setup',
        '/testing/testcafe-db-teardown'
    )

    @staticmethod
    def lookup_auth_dependency(route):
        # Check if auth dependency exists
        return any(d.dependency == auth for d in route.dependencies)

    def test_ensure_endpoints_depend_on_oidc_auth_function(self):
        # A little risky since we should avoid "logic" in the test code!
        # (so direct auth "requests" tests added in class below)

        # Loop through all FastAPI routes (except the ones from the above
        # exclude list) and make sure they depend (via fastapi.Depends) on the
        # auth function in the mora.auth.keycloak.oidc sub-module.

        # Skip the starlette.routing.Route's (defined by the framework)
        routes = filter(
            lambda route: isinstance(route, fastapi.routing.APIRoute),
            main.app.routes
        )
        # Only check endpoints not in the NO_AUTH_ENDPOINTS list
        routes = filter(
            lambda route: route.path not in TestServiceAuth.NO_AUTH_ENDPOINTS,
            routes
        )

        has_auth = map(TestServiceAuth.lookup_auth_dependency, routes)
        self.assertTrue(all(has_auth))

    def test_ensure_no_auth_endpoints_do_not_depend_on_auth_function(self):
        no_auth_routes = filter(
            lambda route: route.path in TestServiceAuth.NO_AUTH_ENDPOINTS,
            main.app.routes
        )

        has_auth = map(TestServiceAuth.lookup_auth_dependency, no_auth_routes)
        self.assertFalse(any(has_auth))


class TestAuthEndpointsReturn401(tests.cases.TestCase):

    def setUp(self):
        super().setUp()
        # Enable the real OIDC auth function
        self.app.dependency_overrides = []

    def test_auth_service_address(self):
        self.assertRequestFails(
            '/service/e/00000000-0000-0000-0000-000000000000/details/address',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_cpr(self):
        self.assertRequestFails(
            '/service/e/cpr_lookup/?q=1234',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_details_reading(self):
        self.assertRequestFails(
            '/service/e/00000000-0000-0000-0000-000000000000/details/',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_details_writing(self):
        self.assertRequestResponse(
            '/service/details/create',
            {'msg': 'Unauthorized'},
            status_code=HTTP_401_UNAUTHORIZED,
            json=[{'not': 'important'}]
        )

    def test_auth_service_employee(self):
        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/e/',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_exports(self):
        self.assertRequestFails(
            '/service/exports/not-important',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_facets(self):
        self.assertRequestFails(
            '/service/c/ancestor-tree',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_integration_data(self):
        self.assertRequestFails(
            '/service/ou'
            '/00000000-0000-0000-0000-000000000000/integration-data',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_itsystem(self):
        self.assertRequestFails(
            '/service/o/00000000-0000-0000-0000-000000000000/it/',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_kle(self):
        # KLE router not used anywhere?
        pass

    def test_auth_service_org(self):
        self.assertRequestFails(
            '/service/o/',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_orgunit(self):
        self.assertRequestFails(
            '/service/ou/00000000-0000-0000-0000-000000000000/children',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_related(self):
        self.assertRequestFails(
            '/service/ou/00000000-0000-0000-0000-000000000000/map',
            HTTP_401_UNAUTHORIZED,
            json=[{'not': 'important'}]
        )

    def test_auth_service_configuration(self):
        self.assertRequestFails(
            '/service/ou/00000000-0000-0000-0000-000000000000/configuration',
            HTTP_401_UNAUTHORIZED
        )

    def test_auth_service_validate(self):
        self.assertRequestFails(
            '/service/validate/org-unit/',
            HTTP_401_UNAUTHORIZED,
            json=[{'not': 'important'}]
        )

    def test_auth_api_v1(self):
        self.assertRequestFails(
            '/api/v1/it',
            HTTP_401_UNAUTHORIZED
        )


class TestAuthEndpointsReturn2xx(tests.cases.LoRATestCase):
    """
    Keycloak integration tests of a few endpoints (one from /service endpoints
    and one from the /api/v1 endpoints)
    """

    def setUp(self):
        super().setUp()
        # Enable the real Keycloak auth mechanism in order to perform Keycloak
        # integration tests
        self.app.dependency_overrides = []

    def test_auth_service_org(self):
        self.load_sample_structures(minimal=True)
        self.assertRequest(
            '/service/o/',
            HTTP_200_OK,
            set_auth_header=True
        )

    def test_auth_api_v1(self):
        self.assertRequest(
            '/api/v1/it',
            HTTP_200_OK,
            set_auth_header=True
        )

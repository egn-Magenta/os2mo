# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from tests import util
from unittest.mock import patch

import tests.cases
from mora import exceptions
from mora.service.address_handler import www


async def async_facet_get_one_class(x, y, *args, **kwargs):
    return {"uuid": y}


@patch("mora.service.facet.get_one_class", new=async_facet_get_one_class)
class WWWAddressHandlerTests(tests.cases.AsyncMockRequestContextTestCase):
    handler = www.WWWAddressHandler
    visibility = "dd5699af-b233-44ef-9107-7a37016b2ed1"
    value = "http://www.test.org/"

    async def test_from_effect(self):
        # Arrange
        value = "http://www.test.org/"

        effect = {
            "relationer": {"adresser": [{"urn": "urn:magenta.dk:www:{}".format(value)}]}
        }

        address_handler = await self.handler.from_effect(effect)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    async def test_from_request(self):
        # Arrange
        value = "http://www.test.org/"

        request = {"value": value}
        address_handler = await self.handler.from_request(request)

        # Act
        actual_value = address_handler.value

        # Assert
        self.assertEqual(value, actual_value)

    async def test_get_mo_address(self):
        # Arrange
        value = "http://www.test.org/"
        address_handler = self.handler(value, self.visibility)

        expected = {
            "href": None,
            "name": "http://www.test.org/",
            "value": "http://www.test.org/",
            "value2": None,
            "visibility": {"uuid": "dd5699af-b233-44ef-9107-7a37016b2ed1"},
        }

        # Act
        actual = await address_handler.get_mo_address_and_properties()

        # Assert
        self.assertEqual(expected, actual)

    def test_get_lora_address(self):
        # Arrange
        value = "http://www.test.org/"
        address_handler = self.handler(value, None)

        expected = {
            "objekttype": "WWW",
            "urn": "urn:magenta.dk:www:http://www.test.org/",
        }

        # Act
        actual = address_handler.get_lora_address()

        # Assert
        self.assertEqual(expected, actual)

    async def test_validation_fails_on_invalid_value(self):
        # Arrange
        value = "@$@#$@#$"  # Not a valid URL

        # Act & Assert
        with self.assertRaises(exceptions.HTTPException):
            await self.handler.validate_value(value)

    async def test_validation_succeeds_on_correct_values(self):
        # Arrange
        valid_values = [
            "http://www.test.com",
            "https://www.test.com",
            "http://subdomain.hej.com/welcome/to/test.html",
        ]

        # Act & Assert
        for value in valid_values:
            # Shouldn't raise exception
            await self.handler.validate_value(value)

    async def test_validation_succeeds_with_force(self):
        # Arrange
        value = "GARBAGEGARBAGE"  # Not a valid URL

        # Act & Assert
        with util.patch_query_args({"force": "1"}):
            await self.handler.validate_value(value)

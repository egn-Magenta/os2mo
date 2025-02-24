# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import tests.cases


class Tests(tests.cases.TestCase):
    maxDiff = None

    def test_create_invalid_type(self):
        self.assertRequestResponse(
            "/service/details/create",
            {
                "description": "Unknown role type.",
                "error": True,
                "error_key": "E_UNKNOWN_ROLE_TYPE",
                "status": 400,
                "types": ["kaflaflibob"],
            },
            json=[
                {
                    "type": "kaflaflibob",
                }
            ],
            status_code=400,
        )

    def test_edit_invalid_type(self):
        self.assertRequestResponse(
            "/service/details/edit",
            {
                "description": "Unknown role type.",
                "error": True,
                "error_key": "E_UNKNOWN_ROLE_TYPE",
                "status": 400,
                "types": ["kaflaflibob"],
            },
            json=[
                {
                    "type": "kaflaflibob",
                }
            ],
            status_code=400,
        )

    def test_invalid_json(self):
        self.assertRequestResponse(
            "/service/details/edit",
            {
                "description": "Invalid input.",
                "error": True,
                "error_key": "E_INVALID_INPUT",
                "request": "kaflaflibob",
                "status": 400,
            },
            json="kaflaflibob",
            status_code=400,
        )

    def test_request_invalid_type(self):
        self.assertRequestResponse(
            "/service/e/00000000-0000-0000-0000-000000000000/details/blyf",
            {
                "description": "Unknown role type.",
                "error": True,
                "error_key": "E_UNKNOWN_ROLE_TYPE",
                "status": 400,
                "type": "blyf",
            },
            status_code=400,
        )

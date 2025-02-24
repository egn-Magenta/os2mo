# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from uuid import UUID
import unittest

import mora.auth.keycloak.uuid_extractor as extractors


class TestExtractUuidsFromAncestorTree(unittest.TestCase):
    def test_return_set_of_uuids(self):
        tree = [
            {
                "name": "Kolding Kommune",
                "user_key": "Kolding Kommune",
                "uuid": "f06ee470-9f17-566f-acbe-e938112d46d9",
                "validity": {"from": "1960-01-01", "to": None},
                "children": [
                    {
                        "name": "Teknik og Miljø",
                        "user_key": "Teknik og Miljø",
                        "uuid": "23a2ace2-52ca-458d-bead-d1a42080579f",
                        "validity": {"from": "1960-01-01", "to": None},
                        "children": [
                            {
                                "name": "Renovation",
                                "user_key": "Renovation",
                                "uuid": "dac3b1ef-3d36-4464-9839-f611a4215cb5",
                                "validity": {"from": "1960-01-01", "to": None},
                            }
                        ],
                    }
                ],
            }
        ]

        self.assertSetEqual(
            {
                UUID("f06ee470-9f17-566f-acbe-e938112d46d9"),
                UUID("23a2ace2-52ca-458d-bead-d1a42080579f"),
                UUID("dac3b1ef-3d36-4464-9839-f611a4215cb5"),
            },
            extractors.get_ancestor_uuids(tree),
        )

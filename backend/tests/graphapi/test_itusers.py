# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch
from ramodels.mo.details import ITUserRead

import mora.graphapi.dataloaders as dataloaders
from mora.graphapi.main import get_schema

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestItusersQuery:
    """Class collecting itusers query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(ITUserRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the ituser data model."""

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "search_role_type", patch_loader(test_data))
            query = """
                query {
                    itusers {
                        employee_uuid
                        itsystem_uuid
                        org_unit_uuid
                        type
                        validity {from to}
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["itusers"] == [
            {
                "employee_uuid": ituser["employee_uuid"],
                "itsystem_uuid": ituser["itsystem_uuid"],
                "org_unit_uuid": ituser["org_unit_uuid"],
                "type": ituser["type"],
                "validity": ituser["validity"],
            }
            for ituser in test_data
        ]

    @given(test_data=st.lists(st.builds(ITUserRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test, patch_loader):
        """Test that we can query itusers by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # JSON encode test data
        test_data = jsonable_encoder(test_data)

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(dataloaders, "get_role_type_by_uuid", patch_loader(test_data))
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        itusers(uuids: $uuids) {
                            uuid
                        }
                    }
                """
            response = graphapi_test.post(
                "/graphql", json={"query": query, "variables": {"uuids": test_uuids}}
            )

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None

        # Check UUID equivalence
        result_uuids = [assoc.get("uuid") for assoc in data["itusers"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))

# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch
from ramodels.mo import FacetRead

import mora.graphapi.dataloaders as dataloaders
import mora.graphapi.main as main
from mora.graphapi.main import get_schema

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------

SCHEMA = str(get_schema())


class TestFacetsQuery:
    """Class collecting facets query tests.

    Data loaders are mocked to return specific values, generated via
    Hypothesis.
    MonkeyPatch.context is used as a context manager to achieve this,
    because mocks are *not* reset between invocations of Hypothesis examples.
    """

    @given(test_data=st.lists(st.builds(FacetRead)))
    def test_query_all(self, test_data, graphapi_test, patch_loader):
        """Test that we can query all attributes of the facets data model."""

        # patch get_facets to return list(ClassRead)
        with MonkeyPatch.context() as patch:
            patch.setattr(main, "get_facets", patch_loader(test_data))
            query = """
                query {
                    facets {
                        parent_uuid
                        org_uuid
                        published
                        type
                        uuid
                    }
                }
            """
            response = graphapi_test.post("/graphql", json={"query": query})

        data, errors = response.json().get("data"), response.json().get("errors")
        assert errors is None
        assert data is not None
        assert data["facets"] == [
            {
                "parent_uuid": facet["parent_uuid"],
                "org_uuid": facet["org_uuid"],
                "published": facet["published"],
                "type": facet["type"],
                "uuid": facet["uuid"],
            }
            # convert the test_data to json
            for facet in jsonable_encoder(test_data)
        ]

    @given(test_data=st.lists(st.builds(FacetRead)), st_data=st.data())
    def test_query_by_uuid(self, test_data, st_data, graphapi_test):
        """Test that we can query facets by UUID."""

        # Sample UUIDs
        uuids = [str(model.uuid) for model in test_data]
        test_uuids = st_data.draw(st.lists(st.sampled_from(uuids))) if uuids else []

        # Patch dataloader
        with MonkeyPatch.context() as patch:
            patch.setattr(
                dataloaders,
                "lora_facets_to_mo_facets",
                lambda *args, **kwargs: test_data,
            )
            query = """
                    query TestQuery($uuids: [UUID!]) {
                        facets(uuids: $uuids) {
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
        result_uuids = [assoc.get("uuid") for assoc in data["facets"]]
        assert set(result_uuids) == set(test_uuids)
        assert len(result_uuids) == len(set(test_uuids))

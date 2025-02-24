# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os

import pytest
from aioresponses import aioresponses as aioresponses_
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from hypothesis import Verbosity
from hypothesis.database import InMemoryExampleDatabase
from starlette_context import _request_scope_context_storage
from starlette_context.ctx import _Context

from mora.api.v1.models import Validity
from tests.util import load_sample_structures, _mox_testing_api
from tests.hypothesis_utils import validity_model_strat

h_db = InMemoryExampleDatabase()
h_settings.register_profile("ci", max_examples=100, deadline=None, database=h_db)
h_settings.register_profile("dev", max_examples=10, database=h_db)
h_settings.register_profile(
    "debug", max_examples=10, verbosity=Verbosity.verbose, database=h_db
)
h_settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))


def pytest_runtest_setup(item):
    print(os.environ.items())
    os.environ["PYTEST_RUNNING"] = "True"


def pytest_configure(config):
    config.addinivalue_line("markers", "serial: mark test to run serially")


st.register_type_strategy(Validity, validity_model_strat())


@pytest.fixture(autouse=True)
def mocked_context(monkeypatch) -> _Context:
    """
    Testing code that relies on context vars without a full test client / app.
    Originally inspired by this solution from the author of starlette-context:
    https://github.com/tomwojcik/starlette-context/issues/46#issuecomment-867148272.
    """

    @property
    def data(self) -> dict:
        """
        The original _Context.data method, but returns an empty dict on error.
        """
        try:
            return _request_scope_context_storage.get()
        except LookupError:
            return {}

    monkeypatch.setattr(_Context, "data", data)
    return _Context()


@pytest.fixture
def aioresponses():
    """Pytest fixture for aioresponses."""
    with aioresponses_() as aior:
        yield aior


@pytest.fixture(scope="class")
def testing_db():
    _mox_testing_api("db-setup")
    yield
    _mox_testing_api("db-teardown")


@pytest.fixture
async def sample_structures(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=False)
    yield
    _mox_testing_api("db-reset")


@pytest.fixture
async def sample_structures_minimal(testing_db):
    """Function scoped fixture, which is called on every test with a teardown"""
    await load_sample_structures(minimal=True)
    yield
    _mox_testing_api("db-reset")

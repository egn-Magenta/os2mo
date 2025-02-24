#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any
from typing import Dict

from graphql import GraphQLSchema
from graphql import utilities as gql_util
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from pydantic import BaseSettings

try:
    from mora.graphapi.main import get_schema
except ImportError:
    raise ImportError(
        "Could not import mora.graphapi. "
        "This script is meant to run in a MO docker image context."
    )

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------

ROOT_PATH = Path(__file__).parent


class Settings(BaseSettings):
    out: Path = ROOT_PATH / "voyager.html"
    search_path: Path = ROOT_PATH


def main() -> None:
    settings = Settings()

    # Get introspection from loaded schema
    schema: GraphQLSchema = gql_util.build_schema(get_schema().as_str())
    introspect: Dict[str, Any] = gql_util.introspection_from_schema(schema)

    # Apply to template & write out
    template: Template = Environment(
        loader=FileSystemLoader(searchpath=settings.search_path)
    ).get_template("voyager.j2")
    settings.out.write_text(
        template.render(introspection_json=json.dumps({"data": introspect}))
    )


if __name__ == "__main__":
    main()

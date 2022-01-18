#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""GraphQL executer with the necessary context variables.

Used for shimming the service API.
"""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


async def execute_graphql(*args, **kwargs):
    from mora.graphapi.main import get_schema
    from mora.graphapi.dataloaders import get_loaders
    from mora.graphapi.middleware import set_is_shim

    set_is_shim()

    loaders = await get_loaders()

    return await get_schema().execute(*args, **kwargs, context_value=loaders)

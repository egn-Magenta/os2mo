# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import collections
import re
import uuid
from typing import Any
from typing import Dict
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter
from fastapi import Query

from . import facet
from . import handlers
from . import org
from .address_handler import base
from .validation import validator
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..triggers import Trigger
from ..util import ensure_list

client = httpx.AsyncClient(
    headers={
        "User-Agent": "MORA/0.1",
    }
)

MUNICIPALITY_CODE_PATTERN = re.compile(r"urn:dk:kommune:(\d+)")

router = APIRouter()


async def get_address_type(effect):
    c = common.get_connector()
    address_type_uuid = mapping.ADDRESS_TYPE_FIELD(effect)[0].get("uuid")
    only_primary_uuid = util.get_args_flag("only_primary_uuid")

    return await facet.get_one_class(
        c, address_type_uuid, only_primary_uuid=only_primary_uuid
    )


async def get_one_address(effect, only_primary_uuid: bool = False) -> Dict[Any, Any]:
    scope = mapping.SINGLE_ADDRESS_FIELD(effect)[0].get("objekttype")
    handler = await base.get_handler_for_scope(scope).from_effect(effect)

    return await handler.get_mo_address_and_properties(only_primary_uuid)


@router.get("/o/{orgid}/address_autocomplete/")
# @util.restrictargs('global', required=['q'])
async def address_autocomplete(
    orgid: UUID, q: str, global_lookup: Optional[bool] = Query(False, alias="global")
):
    """Perform address autocomplete, resolving both ``adgangsadresse`` and
    ``adresse``.

    :param orgid: The UUID of the organisation

    .. :quickref: Address; Autocomplete

    :queryparam str q: A query string to be used for lookup
    :queryparam boolean global: Whether or not the lookup should be in
        the entire country, or contained to the municipality of the
        organisation

    **Example Response**:

    :<jsonarr uuid uuid: A UUID of a DAR address
    :<jsonarr str name: A human readable name for the address

    .. sourcecode:: json

      [
        {
          "location": {
            "uuid": "f0396d0f-ef2d-41e5-a420-b4507b26b6fa",
            "name": "Rybergsvej 1, Sønderby, 5631 Ebberup"
          }
        },
        {
          "location": {
            "uuid": "0a3f50cb-05eb-32b8-e044-0003ba298018",
            "name": "Wild Westvej 1, 9310 Vodskov"
          }
        }
      ]

    """
    orgid = str(orgid)

    if not global_lookup:
        org = await common.get_connector().organisation.get(orgid)

        if not org:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()

        for myndighed in org.get("relationer", {}).get("myndighed", []):
            m = MUNICIPALITY_CODE_PATTERN.fullmatch(myndighed.get("urn"))

            if m:
                code = int(m.group(1))
                break
        else:
            exceptions.ErrorCodes.E_NO_LOCAL_MUNICIPALITY()
    else:
        code = None

    #
    # In order to allow reading both access & regular addresses, we
    # autocomplete both into an ordered dictionary, with the textual
    # representation as keys. Regular addresses tend to be less
    # relevant than access addresses, so we list them last.
    #
    # The limits are somewhat arbitrary: Since access addresses mostly
    # differ by street number or similar, we only show five -- by
    # comparison, ten addresses seems apt since they may refer to
    # apartments etc.
    #

    async def get_access_addreses() -> list[dict]:
        params = {
            "per_side": 5,
            "noformat": "1",
            "q": q,
        }
        if code is not None:
            params["kommunekode"] = code

        r = await client.get(
            "https://api.dataforsyningen.dk/adgangsadresser/autocomplete",
            params=params,
        )
        return r.json()

    addrs = collections.OrderedDict(
        (addr["tekst"], addr["adgangsadresse"]["id"])
        for addr in await get_access_addreses()
    )

    async def get_addresses() -> list[dict]:
        params = {
            "per_side": 10,
            "noformat": "1",
            "q": q,
        }
        if code is not None:
            params["kommunekode"] = code

        r = await client.get(
            "https://api.dataforsyningen.dk/adresser/autocomplete",
            params=params,
        )
        return r.json()

    for addr in await get_addresses():
        addrs.setdefault(addr["tekst"], addr["adresse"]["id"])

    return [
        {
            "location": {
                "name": k,
                "uuid": addrs[k],
            },
        }
        for k in addrs
    ]


class AddressRequestHandler(handlers.OrgFunkRequestHandler):
    role_type = mapping.ADDRESS
    function_key = mapping.ADDRESS_KEY

    async def prepare_create(self, req):
        org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=False)

        employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=False)

        engagement_uuid = util.get_mapping_uuid(req, mapping.ENGAGEMENT, required=False)

        number_of_uuids = len(
            list(
                filter(
                    lambda x: x is not None,
                    [org_unit_uuid, employee_uuid, engagement_uuid],
                )
            )
        )

        if number_of_uuids != 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                f"Must supply exactly one {mapping.ORG_UNIT} UUID, "
                f"{mapping.PERSON} UUID or {mapping.ENGAGEMENT} UUID",
                obj=req,
            )

        valid_from, valid_to = util.get_validities(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        address_type_uuid = util.get_mapping_uuid(
            req, mapping.ADDRESS_TYPE, required=True
        )

        c = lora.Connector()
        only_primary_uuid = util.get_args_flag("only_primary_uuid")

        type_obj = await facet.get_one_class(
            c, address_type_uuid, only_primary_uuid=only_primary_uuid
        )

        scope = util.checked_get(type_obj, "scope", "", required=True)

        handler = await base.get_handler_for_scope(scope).from_request(req)

        func_id = util.get_uuid(req, required=False) or str(uuid.uuid4())
        bvn = handler.name or func_id

        # Validation
        if org_unit_uuid:
            await validator.is_date_range_in_org_unit_range(
                req[mapping.ORG_UNIT], valid_from, valid_to
            )

        if employee_uuid:
            await validator.is_date_range_in_employee_range(
                req[mapping.PERSON], valid_from, valid_to
            )

        lora_addr = handler.get_lora_address()
        addresses = ensure_list(lora_addr)

        func = common.create_organisationsfunktion_payload(
            funktionsnavn=mapping.ADDRESS_KEY,
            valid_from=valid_from,
            valid_to=valid_to,
            brugervendtnoegle=bvn,
            funktionstype=address_type_uuid,
            adresser=addresses,
            tilknyttedebrugere=[employee_uuid] if employee_uuid else [],
            tilknyttedeorganisationer=[org_uuid],
            tilknyttedeenheder=[org_unit_uuid] if org_unit_uuid else [],
            tilknyttedefunktioner=[
                common.associated_orgfunc(
                    uuid=engagement_uuid, orgfunc_type=mapping.MoOrgFunk.ENGAGEMENT
                )
            ]
            if engagement_uuid
            else [],
            opgaver=handler.get_lora_properties(),
        )

        self.payload = func
        self.uuid = func_id
        self.trigger_dict.update(
            {Trigger.EMPLOYEE_UUID: employee_uuid, Trigger.ORG_UNIT_UUID: org_unit_uuid}
        )

    async def prepare_edit(self, req: dict):
        function_uuid = util.get_uuid(req)

        # Get the current org-funktion which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.organisationfunktion.get(uuid=function_uuid)

        if not original:
            exceptions.ErrorCodes.E_NOT_FOUND()

        # Get org unit uuid for validation purposes
        org_unit_uuid = mapping.ASSOCIATED_ORG_UNIT_FIELD.get_uuid(original)

        # Get employee uuid for validation purposes
        employee_uuid = mapping.USER_FIELD.get_uuid(original)

        data = req.get("data")
        new_from, new_to = util.get_validities(data)

        payload = {
            "note": "Rediger Adresse",
        }

        number_of_uuids = len(
            list(
                filter(
                    lambda x: x is not None,
                    [
                        data.get(mapping.PERSON),
                        data.get(mapping.ORG_UNIT),
                        data.get(mapping.ENGAGEMENT),
                    ],
                )
            )
        )

        if number_of_uuids > 1:
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                f"Must supply at most one of {mapping.ORG_UNIT} UUID, "
                f"{mapping.PERSON} UUID and {mapping.ENGAGEMENT} UUID",
                obj=req,
            )

        original_data = req.get("original")
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "organisationfunktiongyldighed"),
            )

        update_fields = [
            # Always update gyldighed
            (mapping.ORG_FUNK_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}),
        ]

        if mapping.PERSON in data:
            employee_uuid = util.get_mapping_uuid(data, mapping.PERSON)
            update_fields.append(
                (
                    mapping.USER_FIELD,
                    {
                        "uuid": employee_uuid,
                    },
                )
            )

        if mapping.ORG_UNIT in data:
            org_unit_uuid = util.get_mapping_uuid(data, mapping.ORG_UNIT)

            update_fields.append(
                (
                    mapping.ASSOCIATED_ORG_UNIT_FIELD,
                    {
                        "uuid": org_unit_uuid,
                    },
                )
            )

        if mapping.ENGAGEMENT in data:
            update_fields.append(
                (
                    mapping.ASSOCIATED_FUNCTION_FIELD,
                    {
                        "uuid": util.get_mapping_uuid(data, mapping.ENGAGEMENT),
                        mapping.OBJECTTYPE: mapping.ENGAGEMENT,
                    },
                )
            )

        try:
            attributes = mapping.ORG_FUNK_EGENSKABER_FIELD(original)[-1].copy()
        except (TypeError, LookupError):
            attributes = {}
        new_attributes = {}

        if mapping.USER_KEY in data:
            new_attributes["brugervendtnoegle"] = util.checked_get(
                data, mapping.USER_KEY, ""
            )

        if new_attributes:
            update_fields.append(
                (
                    mapping.ORG_FUNK_EGENSKABER_FIELD,
                    {**attributes, **new_attributes},
                )
            )

        if mapping.VALUE in data:

            address_type_uuid = util.get_mapping_uuid(
                data, mapping.ADDRESS_TYPE, required=True
            )
            only_primary_uuid = util.get_args_flag("only_primary_uuid")

            type_obj = await facet.get_one_class(
                c, address_type_uuid, only_primary_uuid=only_primary_uuid
            )
            scope = util.checked_get(type_obj, "scope", "", required=True)

            handler = await base.get_handler_for_scope(scope).from_request(data)
            lora_addr = handler.get_lora_address()
            if isinstance(lora_addr, list):
                update_fields.extend(
                    map(lambda x: (mapping.ADDRESSES_FIELD, x), lora_addr)
                )

            else:
                update_fields.append(
                    (
                        mapping.SINGLE_ADDRESS_FIELD,
                        lora_addr,
                    )
                )

            update_fields.append(
                (mapping.ADDRESS_TYPE_FIELD, {"uuid": address_type_uuid})
            )

            for prop in handler.get_lora_properties():
                update_fields.append((mapping.VISIBILITY_FIELD, prop))

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.ADDRESS_FIELDS.difference(
                {x[0] for x in update_fields},
            )
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )
        self.payload = payload
        self.uuid = function_uuid
        self.trigger_dict.update(
            {Trigger.ORG_UNIT_UUID: org_unit_uuid, Trigger.EMPLOYEE_UUID: employee_uuid}
        )

        if employee_uuid:
            await validator.is_date_range_in_employee_range(
                {"uuid": employee_uuid}, new_from, new_to
            )

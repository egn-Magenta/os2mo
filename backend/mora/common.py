# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""Common LoRA logic
-----------------

This module provides various methods and classes for representing or
creating LoRA objects from our object representations. Although
similar to py:module:`mora.util`, they aren't mere utility methods, and
can have deep knowledge of how we expect LoRA to behave.

"""
import collections
import copy
import datetime
import functools
import json
import typing
import uuid
from typing import Union

import werkzeug
from starlette.requests import HTTPConnection
from starlette.requests import Request
from starlette_context import context
from starlette_context.plugins import Plugin

from . import exceptions
from . import lora
from . import mapping
from . import util
from .exceptions import ErrorCodes
from .mapping import OwnerInferencePriority


class LoRaConnectorPlugin(Plugin):
    """
    Startlette Context Plugin to cache the LoRa Connector on a request-basis.
    """

    key = "lora_connector"

    async def process_request(
        self, request: Union[Request, HTTPConnection]
    ) -> typing.Optional[typing.Any]:
        @functools.lru_cache()
        def cached_create_connector(**kwargs):
            return _create_connector(**kwargs)

        return cached_create_connector


def get_connector(**loraparams) -> lora.Connector:
    create_connector = context.get(LoRaConnectorPlugin.key, _create_connector)
    return create_connector(**loraparams)


def _create_connector(**loraparams) -> lora.Connector:
    args = util.get_query_args() or {}

    if args.get("at"):
        loraparams["effective_date"] = util.from_iso_time(args["at"])

    if "validity" in args:
        if "/" in args["validity"]:
            try:
                start, end = args["validity"].split("/")
            except ValueError:
                exceptions.ErrorCodes.V_INVALID_VALIDITY(validity=args["validity"])
            else:
                loraparams["validity"] = "present"
                loraparams["virkningfra"] = start
                loraparams["virkningtil"] = end
        else:
            loraparams["validity"] = args["validity"]

    return lora.Connector(**loraparams)


class cache(collections.defaultdict):
    """combination of functools.partial & defaultdict into one"""

    def __init__(self, func, *args, **kwargs):
        super().__init__(functools.partial(func, *args, **kwargs))

    def __missing__(self, key):
        v = self[key] = self.default_factory(key)
        return v


def inactivate_old_interval(
    old_from: str, old_to: str, new_from: str, new_to: str, payload: dict, path: tuple
) -> dict:
    """
    Create 'inactivation' updates based on two sets of from/to dates

    :param old_from: The old 'from' time, in ISO-8601
    :param old_to: The old 'to' time, in ISO-8601
    :param new_from: The new 'from' time, in ISO-8601
    :param new_to: The new 'to' time, in ISO-8601
    :param payload: An existing payload to add the updates to
    :param path: The path to where the object's 'gyldighed' is located

    :return: The payload with the inactivation updates added, if relevant
    """
    if old_from < new_from:
        val = {"gyldighed": "Inaktiv", "virkning": _create_virkning(old_from, new_from)}
        payload = util.set_obj_value(payload, path, [val])
    if new_to < old_to:
        val = {"gyldighed": "Inaktiv", "virkning": _create_virkning(new_to, old_to)}
        payload = util.set_obj_value(payload, path, [val])
    return payload


def ensure_bounds(
    valid_from: datetime.datetime,
    valid_to: datetime.datetime,
    props: typing.List[mapping.FieldTuple],
    obj: dict,
    payload: dict,
):
    for field in props:
        props = util.get_obj_value(obj, field.path, field.filter_fn)
        if not props:
            continue

        updated_props = []  # type: typing.List[mapping.FieldTuple]
        if field.type == mapping.FieldTypes.ADAPTED_ZERO_TO_MANY:
            # If adapted zero-to-many, move first and last, and merge
            sorted_props = sorted(props, key=util.get_effect_from)
            first = sorted_props[0]
            last = sorted_props[-1]

            # Check bounds on first
            if valid_from < util.get_effect_from(first):
                first["virkning"]["from"] = util.to_lora_time(valid_from)
                updated_props = sorted_props
            if util.get_effect_to(last) < valid_to:
                last["virkning"]["to"] = util.to_lora_time(valid_to)
                updated_props = sorted_props

        elif field.type == mapping.FieldTypes.ZERO_TO_MANY:
            # Don't touch virkninger on zero-to-many
            updated_props = props
        else:
            # Zero-to-one. Move first and last. LoRa does the merging.
            sorted_props = sorted(props, key=util.get_effect_from)
            first = sorted_props[0]
            last = sorted_props[-1]

            if valid_from < util.get_effect_from(first):
                first["virkning"]["from"] = util.to_lora_time(valid_from)
                updated_props.append(first)
            if util.get_effect_to(last) < valid_to:
                last["virkning"]["to"] = util.to_lora_time(valid_to)
                if not updated_props or last is not first:
                    updated_props.append(last)

        if updated_props:
            payload = util.set_obj_value(payload, field.path, updated_props)
    return payload


def update_payload(
    valid_from: datetime.datetime,
    valid_to: datetime.datetime,
    relevant_fields: typing.List[typing.Tuple[mapping.FieldTuple, dict]],
    obj: dict,
    payload: dict,
):
    relevant_fields = copy.deepcopy(relevant_fields)
    combined_fields = werkzeug.datastructures.OrderedMultiDict(relevant_fields)

    for field_tuple, vals in combined_fields.lists():
        for val in vals:
            val["virkning"] = _create_virkning(valid_from, valid_to)

        # Get original properties
        props = util.get_obj_value(obj, field_tuple.path, field_tuple.filter_fn)

        if field_tuple.type == mapping.FieldTypes.ADAPTED_ZERO_TO_MANY:
            # 'Fake' zero-to-one relation. Merge into existing list.
            updated_props = _merge_obj_effects(props, vals)
        elif field_tuple.type == mapping.FieldTypes.ZERO_TO_MANY:
            # Actual zero-to-many relation. Just append.
            updated_props = vals
        else:
            # Zero-to-one relation - LoRa does the merging for us,
            # so disregard existing props
            assert 0 <= len(vals) <= 1
            updated_props = vals

        for p in updated_props:
            # TODO: Fix this when the underlying bug in LoRa is resolved
            # https://redmine.magenta-aps.dk/issues/31576
            if len(p) == 1 and "virkning" in p and "relationer" in field_tuple.path[0]:
                p["uuid"] = ""
                p["urn"] = ""
        payload = util.set_obj_value(payload, field_tuple.path, updated_props)

    return payload


def _merge_obj_effects(
    orig_objs: typing.List[dict],
    new_objs: typing.List[dict],
) -> typing.List[dict]:
    """
    Performs LoRa-like merging of a relation object, with a current list of
    relation objects, with regards to virkningstider,
    producing a merged list of relation to be inserted into LoRa, similar to
    how LoRa performs merging of zero-to-one relations.

    We currently expect that the list of new objects all have the
    same virkningstid

    :param orig_objs: A list of objects with virkningstider
    :param new_objs: A list of new objects with virkningstider, to be merged
                into the original list. All of the virkningstider
                should be identical.
    :return: A list of merged objects
    """
    result = new_objs

    if orig_objs is None:
        return result

    sorted_orig = sorted(orig_objs, key=util.get_effect_from)

    # sanity checks
    assert len({util.get_effect_to(obj) for obj in new_objs}) == 1
    assert len({util.get_effect_from(obj) for obj in new_objs}) == 1

    new_from = util.get_effect_from(new_objs[0])
    new_to = util.get_effect_to(new_objs[0])

    for orig in sorted_orig:
        orig_from = util.get_effect_from(orig)
        orig_to = util.get_effect_to(orig)

        if new_to <= orig_from or orig_to <= new_from:
            # Not affected, add orig as-is
            # [---New---)
            #             [---Orig---)
            # or
            #              [---New---)
            # [---Orig---)
            result.append(orig)
            continue

        if new_from <= orig_from:
            if orig_to <= new_to:
                # Orig is completely contained in new, ignore orig
                # [------New------)
                #   [---Orig---)
                continue
            else:
                # New end overlaps orig beginning, change orig start time.
                # [---New---)
                #        [---Orig---)
                new_rel = copy.deepcopy(orig)
                new_rel["virkning"]["from"] = util.to_lora_time(new_to)
                result.append(new_rel)
        elif new_from < orig_to:
            # New beginning overlaps with orig end, change orig end time.
            #       [---New---)
            # [---Orig---)
            new_obj_before = copy.deepcopy(orig)
            new_obj_before["virkning"]["to"] = util.to_lora_time(new_from)
            result.append(new_obj_before)
            if new_to < orig_to:
                # New is contained in orig, split orig in two
                #    [---New---)
                # [------Orig------)
                new_obj_after = copy.deepcopy(orig)
                new_obj_after["virkning"]["from"] = util.to_lora_time(new_to)
                result.append(new_obj_after)

    return sorted(result, key=util.get_effect_from)


def _create_virkning(
    valid_from: Union[str, datetime.date, datetime.datetime],
    valid_to: Union[str, datetime.date, datetime.datetime],
) -> dict:
    """
    Create virkning object

    :param valid_from: The "from" date.
    :param valid_to: The "to" date.
    :return: The virkning object.
    """
    return {
        "from": util.to_lora_time(valid_from),
        "to": util.to_lora_time(valid_to),
    }


def _set_virkning(lora_obj: dict, virkning: dict, overwrite=False) -> dict:
    """
    Adds virkning to the "leafs" of the given LoRa JSON (tree) object.

    :param lora_obj: A LoRa object with or without virkning.
    :param virkning: The virkning to set in the LoRa object
    :param overwrite: Whether any original virknings should be overwritten
    :return: The LoRa object with the new virkning

    """
    for v in lora_obj.values():
        if isinstance(v, dict):
            _set_virkning(v, virkning, overwrite)
        elif isinstance(v, list):
            for d in v:
                d.setdefault("virkning", virkning.copy())
    return lora_obj


def inactivate_org_funktion_payload(enddate, note):
    obj_path = ("tilstande", "organisationfunktiongyldighed")
    val_inactive = {
        "gyldighed": "Inaktiv",
        "virkning": _create_virkning(enddate, "infinity"),
    }

    payload = util.set_obj_value({"note": note}, obj_path, [val_inactive])

    return payload


def to_lora_obj(
    value: typing.Union[typing.Dict[str, str], str]
) -> typing.Dict[str, str]:
    """
    transforms values to uniform lora-format
    :param value: (potentially) High-level specification of lora obj
    :return: concrete lora-understandable obj
    """

    if isinstance(value, str):  # if string, assume uuid
        return {mapping.UUID: value}
    elif isinstance(value, dict):  # if dict, do nothing
        if value.keys() <= {mapping.UUID, mapping.OBJECTTYPE}:
            return value
        else:
            raise ValueError(f"unexpected_lora_keys={value.keys()}")
    raise TypeError(f"unexpected type: {type(value)}")


def associated_orgfunc(
    uuid: str, orgfunc_type: mapping.MoOrgFunk
) -> typing.Dict[str, str]:
    """
    creates a lora-understandable object appropriate for
    associating org funcstions with each other

    :param uuid: uuid of the associated orgfunc
    :param orgfunc_type: type of the orgfunc
    :return:
    """
    return {mapping.UUID: uuid, mapping.OBJECTTYPE: orgfunc_type.value}


def create_organisationsfunktion_payload(
    funktionsnavn: str,
    valid_from: str,
    valid_to: str,
    brugervendtnoegle: str,
    tilknyttedeorganisationer: typing.List[str],
    tilknyttedebrugere: typing.Optional[typing.List[str]] = None,
    tilknyttedeenheder: typing.Optional[typing.List[str]] = None,
    tilknyttedefunktioner: typing.Optional[
        typing.List[typing.Union[typing.Dict[str, str], str]]
    ] = None,
    tilknyttedeitsystemer: typing.Optional[typing.List[str]] = None,
    tilknyttedeklasser: typing.Optional[typing.List[str]] = None,
    funktionstype: typing.Optional[str] = None,
    primær: typing.Optional[str] = None,
    opgaver: typing.Optional[typing.List[dict]] = None,
    adresser: typing.Optional[typing.List[dict]] = None,
    fraktion: typing.Optional[str] = None,
    udvidelse_attributter: typing.Optional[dict] = None,
    tilknyttedepersoner: typing.Optional[typing.List[str]] = None,
) -> dict:
    virkning = _create_virkning(valid_from, valid_to)

    org_funk = {
        "note": "Oprettet i MO",
        "attributter": {
            "organisationfunktionegenskaber": [
                {
                    "funktionsnavn": funktionsnavn,
                    "brugervendtnoegle": brugervendtnoegle,
                },
            ],
        },
        "tilstande": {
            "organisationfunktiongyldighed": [
                {
                    "gyldighed": "Aktiv",
                },
            ],
        },
        "relationer": {
            "tilknyttedeorganisationer": [
                {"uuid": uuid} for uuid in tilknyttedeorganisationer
            ]
        },
    }

    if tilknyttedebrugere:
        org_funk["relationer"]["tilknyttedebrugere"] = [
            {
                "uuid": brugerid,
            }
            for brugerid in tilknyttedebrugere
            if brugerid
        ]
    if tilknyttedepersoner:
        org_funk["relationer"]["tilknyttedepersoner"] = [
            {
                "uuid": person_uuid,
            }
            for person_uuid in tilknyttedepersoner
            if person_uuid
        ]
    if tilknyttedeenheder:
        org_funk["relationer"]["tilknyttedeenheder"] = [
            {"uuid": uuid} for uuid in tilknyttedeenheder
        ]

    if tilknyttedefunktioner:
        org_funk["relationer"]["tilknyttedefunktioner"] = list(
            map(to_lora_obj, tilknyttedefunktioner)
        )

    if tilknyttedeitsystemer:
        org_funk["relationer"]["tilknyttedeitsystemer"] = [
            {"uuid": uuid} for uuid in tilknyttedeitsystemer
        ]

    if tilknyttedeklasser:
        org_funk["relationer"]["tilknyttedeklasser"] = [
            {"uuid": uuid} for uuid in tilknyttedeklasser
        ]

    if funktionstype:
        org_funk["relationer"]["organisatoriskfunktionstype"] = [
            {"uuid": funktionstype}
        ]

    if primær:
        org_funk["relationer"]["primær"] = [{"uuid": primær}]

    if opgaver:
        org_funk["relationer"]["opgaver"] = opgaver

    if adresser:
        org_funk["relationer"]["adresser"] = adresser

    extensions = {}
    if fraktion is not None:
        extensions["fraktion"] = fraktion

    if udvidelse_attributter:
        extensions.update(udvidelse_attributter)

    if extensions:
        org_funk["attributter"]["organisationfunktionudvidelser"] = [extensions]

    org_funk = _set_virkning(org_funk, virkning)

    return org_funk


def create_organisationsenhed_payload(
    enhedsnavn: str,
    valid_from: str,
    valid_to: str,
    brugervendtnoegle: str,
    tilhoerer: str,
    enhedstype: str,
    overordnet: str,
    niveau: str = None,
    opmærkning: str = None,
    opgaver: typing.List[dict] = None,
) -> dict:
    virkning = _create_virkning(valid_from, valid_to)

    org_unit = {
        "note": "Oprettet i MO",
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "enhedsnavn": enhedsnavn,
                    "brugervendtnoegle": brugervendtnoegle,
                },
            ],
        },
        "tilstande": {
            "organisationenhedgyldighed": [
                {
                    "gyldighed": "Aktiv",
                },
            ],
        },
        "relationer": {
            "tilhoerer": [{"uuid": tilhoerer}],
            "enhedstype": [{"uuid": enhedstype}],
            "overordnet": [{"uuid": overordnet}],
        },
    }

    if niveau:
        org_unit["relationer"]["niveau"] = [{"uuid": niveau}]

    if opmærkning:
        org_unit["relationer"]["opmærkning"] = [{"uuid": opmærkning}]

    if opgaver:
        org_unit["relationer"]["opgaver"] = opgaver

    org_unit = _set_virkning(org_unit, virkning)

    return org_unit


def create_bruger_payload(
    valid_from: str,
    valid_to: str,
    fornavn: typing.Optional[str],
    efternavn: typing.Optional[str],
    kaldenavn_fornavn: typing.Optional[str],
    kaldenavn_efternavn: typing.Optional[str],
    seniority: typing.Optional[str],
    brugervendtnoegle: str,
    tilhoerer: str,
    cpr: str,
):
    virkning = _create_virkning(valid_from, valid_to)

    user = {
        "note": "Oprettet i MO",
        "attributter": {
            "brugeregenskaber": [
                {
                    "brugervendtnoegle": brugervendtnoegle,
                },
            ],
        },
        "tilstande": {
            "brugergyldighed": [
                {
                    "gyldighed": "Aktiv",
                },
            ],
        },
        "relationer": {
            "tilhoerer": [{"uuid": tilhoerer}],
        },
    }

    if cpr:
        user["relationer"]["tilknyttedepersoner"] = [
            {
                "urn": "urn:dk:cpr:person:{}".format(cpr),
            },
        ]

    extensions = {}
    if fornavn is not None:
        extensions["fornavn"] = fornavn

    if efternavn is not None:
        extensions["efternavn"] = efternavn

    if kaldenavn_fornavn is not None:
        extensions["kaldenavn_fornavn"] = kaldenavn_fornavn

    if kaldenavn_efternavn is not None:
        extensions["kaldenavn_efternavn"] = kaldenavn_efternavn

    if seniority is not None:
        extensions["seniority"] = seniority

    if extensions:
        user["attributter"]["brugerudvidelser"] = [extensions]

    user = _set_virkning(user, virkning)

    return user


def create_klasse_payload(
    valid_from: str,
    valid_to: str,
    bvn: str,
    title: str,
    facet_uuid: uuid.UUID,
    org_uuid: uuid.UUID,
    org_unit_uuid: typing.Optional[uuid.UUID] = None,
    description: typing.Optional[str] = None,
    scope: typing.Optional[str] = None,
    parent_uuid: typing.Optional[uuid.UUID] = None,
) -> dict:
    virkning = _create_virkning(valid_from, valid_to)

    # NOTE: This is used from SD, and should be split out as a library?
    attributter = {
        "klasseegenskaber": [
            {
                "brugervendtnoegle": bvn,
                "titel": title,
                "virkning": virkning,
            }
        ]
    }
    if description:
        attributter["klasseegenskaber"][0]["beskrivelse"] = description
    if scope:
        attributter["klasseegenskaber"][0]["omfang"] = scope
    tilstande = {
        "klassepubliceret": [{"publiceret": "Publiceret", "virkning": virkning}]
    }
    relationer = {
        "facet": [{"uuid": facet_uuid, "virkning": virkning, "objekttype": "Facet"}],
        "overordnetklasse": [
            {"uuid": parent_uuid, "virkning": virkning, "objekttype": "Klasse"}
        ],
        "ansvarlig": [
            {
                "uuid": org_uuid,
                "virkning": virkning,
                "objekttype": "Organisation",
            }
        ],
        "ejer": [
            {
                "uuid": org_unit_uuid,
                "virkning": virkning,
                "objekttype": "OrganisationEnhed",
            }
        ],
    }
    if parent_uuid is None:
        del relationer["overordnetklasse"]
    if org_unit_uuid is None:
        del relationer["ejer"]
    klasse = {
        "attributter": attributter,
        "relationer": relationer,
        "tilstande": tilstande,
    }

    return klasse


def replace_relation_value(
    relations: typing.List[dict], old_entry: dict, new_entry: dict = None
) -> typing.List[dict]:
    old_from = util.get_effect_from(old_entry)
    old_to = util.get_effect_to(old_entry)

    old_urn = old_entry.get("urn")
    old_uuid = old_entry.get("uuid")
    old_type = old_entry.get("objekttype")

    for i, rel in enumerate(relations):
        if (
            util.get_effect_from(rel) == old_from
            and util.get_effect_to(rel) == old_to
            and rel.get("urn") == old_urn
            and rel.get("uuid") == old_uuid
            and rel.get("objekttype") == old_type
        ):
            new_rels = copy.deepcopy(relations)

            if new_entry:
                new_rels[i] = new_entry
            else:
                del new_rels[i]

            return new_rels

    else:
        exceptions.ErrorCodes.E_ORIGINAL_ENTRY_NOT_FOUND()


async def add_history_entry(scope: lora.Scope, id: str, note: str):
    """
    Add a history entry to a given object.
    The idea is to write an update to the employee whenever an object
    associated to him is created or changed, as to easily be able to get an
    overview of the history of the modifications to both the employee
    but also the employee's associated objects.

    We have to make some sort of 'meaningful' change to data to be
    able to update the 'note' field - which for now amounts to just
    updating the virkning notetekst of gyldighed with a garbage value

    :param scope:
    :param id: The UUID of the employee
    :param note: A note to be associated with the entry
    """

    obj = await scope.get(id)
    if not obj:
        exceptions.ErrorCodes.E_NOT_FOUND(path=scope.path, uuid=id)

    unique_string = str(uuid.uuid4())

    payload = {
        "note": note,
        "tilstande": {
            validity_name: [
                util.set_obj_value(validity, ("virkning", "notetekst"), unique_string)
                for validity in validities
            ]
            for validity_name, validities in obj["tilstande"].items()
        },
    }

    await scope.update(payload, id)


def stable_json_dumps(v):
    """like :py:func:`json.dumps()`, but stable."""
    return json.dumps(v, sort_keys=True, allow_nan=False, ensure_ascii=False)


def parse_owner_inference_priority_str(
    inference_priority_candidate: str,
) -> OwnerInferencePriority:
    """
    Attempt at parsing string to Enum, raises on bad input
    :param inference_priority_candidate:
    :return:
    """
    try:
        return OwnerInferencePriority(inference_priority_candidate)
    except ValueError:
        ErrorCodes.E_INVALID_INPUT(
            f"Invalid {mapping.OWNER_INFERENCE_PRIORITY}: "
            f"{inference_priority_candidate}"
        )

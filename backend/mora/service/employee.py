# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""
Employees
---------

This section describes how to interact with employees.

For more information regarding reading relations involving employees, refer to
http:get:`/service/(any:type)/(uuid:id)/details/`

"""
import asyncio
import copy
import enum
from functools import partial
from operator import contains
from operator import itemgetter
from typing import Any
from typing import Awaitable
from typing import Dict
from typing import Optional
from typing import Union
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from ramodels.base import tz_isodate

from . import autocomplete
from . import handlers
from . import org
from .. import common
from .. import config
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..graphapi.middleware import is_graphql
from ..lora import LoraObjectType
from ..triggers import Trigger
from .validation import validator
from mora.auth.keycloak import oidc
from mora.request_scoped.bulking import request_wide_bulk

router = APIRouter()


@enum.unique
class EmployeeDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with everything except child count
    FULL = 1


class EmployeeRequestHandler(handlers.RequestHandler):
    role_type = "employee"

    async def prepare_create(self, req):
        name = util.checked_get(req, mapping.NAME, "", required=False)
        givenname = util.checked_get(req, mapping.GIVENNAME, "", required=False)
        surname = util.checked_get(req, mapping.SURNAME, "", required=False)

        if name and (surname or givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either name or given name/surame"
            )

        if name:
            givenname = name.rsplit(" ", maxsplit=1)[0]
            surname = name[len(givenname) :].strip()

        if (not name) and (not givenname) and (not surname):
            raise exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
                name="Missing name or givenname or surname"
            )

        nickname_givenname, nickname_surname = self._handle_nickname(req)

        org_uuid = (
            await org.get_configured_organisation(
                util.get_mapping_uuid(req, mapping.ORG, required=False)
            )
        )["uuid"]

        cpr = util.checked_get(req, mapping.CPR_NO, "", required=False)
        userid = util.get_uuid(req, required=False) or str(uuid4())
        bvn = util.checked_get(req, mapping.USER_KEY, userid)
        seniority = req.get(mapping.SENIORITY, None)
        # parse seniority
        if seniority is not None:
            seniority = tz_isodate(seniority).strftime("%Y-%m-%d")

        if cpr:
            try:
                valid_from = util.get_cpr_birthdate(cpr)
            except ValueError as exc:
                settings = config.get_settings()
                if settings.cpr_validate_birthdate:
                    exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr, cause=exc)
                else:
                    valid_from = util.NEGATIVE_INFINITY
        else:
            valid_from = util.NEGATIVE_INFINITY

        valid_to = util.POSITIVE_INFINITY

        if cpr:
            await validator.does_employee_with_cpr_already_exist(
                cpr, valid_from, valid_to, org_uuid, userid
            )

        user = common.create_bruger_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            fornavn=givenname,
            efternavn=surname,
            kaldenavn_fornavn=nickname_givenname,
            kaldenavn_efternavn=nickname_surname,
            seniority=seniority,
            brugervendtnoegle=bvn,
            tilhoerer=org_uuid,
            cpr=cpr,
        )

        details = util.checked_get(req, "details", [])
        details_with_persons = _inject_persons(details, userid, valid_from, valid_to)
        # Validate the creation requests
        self.details_requests = await handlers.generate_requests(
            details_with_persons, mapping.RequestType.CREATE
        )

        self.payload = user
        self.uuid = userid
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = userid

    def _handle_nickname(self, obj: Dict[Union[str, Any], Any]):
        nickname_givenname = obj.get(mapping.NICKNAME_GIVENNAME, None)
        nickname_surname = obj.get(mapping.NICKNAME_SURNAME, None)
        nickname = obj.get(mapping.NICKNAME, None)

        if nickname and (nickname_surname or nickname_givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either nickname or given nickname/surname"
            )
        if nickname:
            nickname_givenname = nickname.rsplit(" ", maxsplit=1)[0]
            nickname_surname = nickname[len(nickname_givenname) :].strip()

        return nickname_givenname, nickname_surname

    async def prepare_edit(self, req: dict):
        original_data = util.checked_get(req, "original", {}, required=False)
        data = util.checked_get(req, "data", {}, required=True)
        userid = util.get_uuid(req, required=False)
        if not userid:
            userid = util.get_uuid(data, fallback=original_data)

        # Get the current org-unit which the user wants to change
        c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
        original = await c.bruger.get(uuid=userid)
        new_from, new_to = util.get_validities(data)

        payload = dict()
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from,
                old_to,
                new_from,
                new_to,
                payload,
                ("tilstande", "brugergyldighed"),
            )

            original_uuid = util.get_mapping_uuid(original_data, mapping.EMPLOYEE)

            if original_uuid and original_uuid != userid:
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    "cannot change employee uuid!",
                )

        update_fields = list()

        # Always update gyldighed
        update_fields.append((mapping.EMPLOYEE_GYLDIGHED_FIELD, {"gyldighed": "Aktiv"}))

        changed_props = {}
        changed_extended_props = {}

        if mapping.USER_KEY in data:
            changed_props["brugervendtnoegle"] = data[mapping.USER_KEY]

        givenname = data.get(mapping.GIVENNAME, "")
        surname = data.get(mapping.SURNAME, "")
        name = data.get(mapping.NAME, "")

        if name and (surname or givenname):
            raise exceptions.ErrorCodes.E_INVALID_INPUT(
                name="Supply either name or given name/surame"
            )
        if name:
            givenname = name.rsplit(" ", maxsplit=1)[0]
            surname = name[len(givenname) :].strip()

        if givenname:
            changed_extended_props["fornavn"] = givenname
        if surname:
            changed_extended_props["efternavn"] = surname

        nickname_givenname, nickname_surname = self._handle_nickname(data)

        seniority = data.get(mapping.SENIORITY, None)

        # clear rather than skip if exists, but value is None
        if seniority is None and mapping.SENIORITY in data:
            seniority = ""

        if nickname_givenname is not None:
            changed_extended_props["kaldenavn_fornavn"] = nickname_givenname
        if nickname_surname is not None:
            changed_extended_props["kaldenavn_efternavn"] = nickname_surname
        if seniority is not None:
            changed_extended_props["seniority"] = seniority

        if changed_props:
            update_fields.append(
                (
                    mapping.EMPLOYEE_EGENSKABER_FIELD,
                    changed_props,
                )
            )

        if changed_extended_props:
            update_fields.append(
                (
                    mapping.EMPLOYEE_UDVIDELSER_FIELD,
                    changed_extended_props,
                )
            )

        if mapping.CPR_NO in data:
            related = mapping.EMPLOYEE_PERSON_FIELD.get(original)
            if related and len(related) > 0:
                attrs = related[-1].copy()
                attrs["urn"] = "urn:dk:cpr:person:{}".format(data[mapping.CPR_NO])
                update_fields.append((mapping.EMPLOYEE_PERSON_FIELD, attrs))

        payload = common.update_payload(
            new_from, new_to, update_fields, original, payload
        )

        bounds_fields = list(
            mapping.EMPLOYEE_FIELDS.difference({x[0] for x in update_fields})
        )
        payload = common.ensure_bounds(
            new_from, new_to, bounds_fields, original, payload
        )
        self.payload = payload
        self.uuid = userid
        self.trigger_dict[Trigger.EMPLOYEE_UUID] = userid

    async def submit(self):
        c = lora.Connector()

        if self.request_type == mapping.RequestType.CREATE:
            self.result = await c.bruger.create(self.payload, self.uuid)
        else:
            self.result = await c.bruger.update(self.payload, self.uuid)

        # process subrequests, if any
        await asyncio.gather(
            *(r.submit() for r in getattr(self, "details_requests", []))
        )

        return await super().submit()


async def __get_employee_from_cache(
    userid: str,
    details: EmployeeDetails = EmployeeDetails.MINIMAL,
    only_primary_uuid: bool = False,
) -> Any:
    """
    Get org unit from cache and process it
    :param userid: uuid of employee
    :param details: configure processing of the employee
    :return: A processed employee
    """
    ret = await get_one_employee(
        c=request_wide_bulk.connector,
        userid=userid,
        user=await request_wide_bulk.get_lora_object(
            type_=LoraObjectType.user, uuid=userid
        )
        if not only_primary_uuid
        else None,
        details=details,
        only_primary_uuid=only_primary_uuid,
    )
    return ret


async def request_bulked_get_one_employee(
    userid: str,
    details: EmployeeDetails = EmployeeDetails.MINIMAL,
    only_primary_uuid: bool = False,
) -> Awaitable:
    """
    EAGERLY adds a uuid to a LAZILY-processed cache. Return an awaitable. Once the
    result is awaited, the FULL cache is processed. Useful to 'under-the-hood' bulk.

    :param userid: uuid of employee
    :param details: configure processing of the employee
    :param only_primary_uuid:
    :return: Awaitable returning the processed employee
    """
    return __get_employee_from_cache(
        userid=userid, details=details, only_primary_uuid=only_primary_uuid
    )


async def get_one_employee(
    c: lora.Connector,
    userid,
    user: Optional[Dict[str, Any]] = None,
    details=EmployeeDetails.MINIMAL,
    only_primary_uuid: bool = False,
):
    if not user:
        user = await c.bruger.get(userid)

        if not user or not util.is_reg_valid(user):
            return None

    if only_primary_uuid:
        # This block could be before the user check, so we would not have to contact
        # LoRa as we can construct the output without during so, however we need to
        # actually validate that the user actually exists to avoid false information.
        return {mapping.UUID: userid}

    props = user["attributter"]["brugeregenskaber"][0]
    extensions = user["attributter"]["brugerudvidelser"][0]

    fornavn = extensions.get("fornavn", "")
    efternavn = extensions.get("efternavn", "")
    kaldenavn_fornavn = extensions.get("kaldenavn_fornavn", "")
    kaldenavn_efternavn = extensions.get("kaldenavn_efternavn", "")
    seniority = extensions.get(mapping.SENIORITY, None)

    r = {
        mapping.GIVENNAME: fornavn,
        mapping.SURNAME: efternavn,
        mapping.NAME: " ".join((fornavn, efternavn)),
        mapping.NICKNAME_GIVENNAME: kaldenavn_fornavn,
        mapping.NICKNAME_SURNAME: kaldenavn_efternavn,
        mapping.NICKNAME: " ".join((kaldenavn_fornavn, kaldenavn_efternavn)).strip(),
        mapping.UUID: userid,
        mapping.SENIORITY: seniority,
    }
    if is_graphql():
        rels = user["relationer"]

        if rels.get("tilknyttedepersoner"):
            cpr = rels["tilknyttedepersoner"][0]["urn"].rsplit(":", 1)[-1]
            r[mapping.CPR_NO] = cpr

        r[mapping.USER_KEY] = props.get("brugervendtnoegle", "")

    if details is EmployeeDetails.FULL:
        rels = user["relationer"]

        if rels.get("tilknyttedepersoner"):
            cpr = rels["tilknyttedepersoner"][0]["urn"].rsplit(":", 1)[-1]
            r[mapping.CPR_NO] = cpr

        r[mapping.ORG] = await org.get_configured_organisation()
        r[mapping.USER_KEY] = props.get("brugervendtnoegle", "")
    elif details is EmployeeDetails.MINIMAL:
        pass  # already done
    return r


@router.get("/e/autocomplete/")
async def autocomplete_employees(query: str):
    settings = config.get_settings()
    return await autocomplete.get_results(
        "bruger", settings.confdb_autocomplete_attrs_employee, query
    )


@router.get("/o/{orgid}/e/")
# @util.restrictargs('at', 'start', 'limit', 'query', 'associated')
async def list_employees(
    orgid: UUID,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    query: Optional[str] = None,
    associated: Optional[bool] = None,
    only_primary_uuid: Optional[bool] = None,
):
    """Query employees in an organisation.

    .. :quickref: Employee; List & search

    :param uuid orgid: UUID of the organisation to search.
        Note: This parameter is now deprecated, and does not affect the result.

    :queryparam date at: Show employees at this point in time,
        in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by employees matching this string.
        Please note that this only applies to attributes of the user, not the
        relations or engagements they have.

    :>json string items: The returned items.
    :>json string offset: Pagination offset.
    :>json string total: Total number of items available on this query.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

     {
       "items": [
         {
           "name": "Knud S\u00f8lvtoft Pedersen",
           "uuid": "059b45b4-7e92-4450-b7ae-dff989d66ad2"
         },
         {
           "name": "Hanna Hede Pedersen",
           "uuid": "74894be9-2476-48e2-8b3a-ba1db926bb0b"
         },
         {
           "name": "Susanne Nybo Pedersen",
           "uuid": "7e79881d-a4ee-4654-904e-4aaa0d697157"
         },
         {
           "name": "Bente Pedersen",
           "uuid": "c9eaffad-971e-4c0c-8516-44c5d29ca092"
         },
         {
           "name": "Vang Overgaard Pedersen",
           "uuid": "f2b9008d-8646-4672-8a91-c12fa897f9a6"
         }
       ],
       "offset": 0,
       "total": 5
     }

    """
    orgid = str(orgid)

    # TODO: share code with list_orgunits?

    c = common.get_connector()

    kwargs = dict(
        limit=limit,
        start=start,
        gyldighed="Aktiv",
    )

    if query:
        if util.is_cpr_number(query):
            kwargs.update(
                tilknyttedepersoner="urn:dk:cpr:person:" + query,
            )
        else:
            query = query
            query = query.split(" ")
            for i in range(0, len(query)):
                query[i] = "%" + query[i] + "%"
            kwargs["vilkaarligattr"] = query

    uuid_filters = []
    # Filter search_result to only show employees with associations
    if associated:
        # NOTE: This call takes ~500ms on fixture-data
        assocs = await c.organisationfunktion.get_all(funktionsnavn="Tilknytning")
        assocs = map(itemgetter(1), assocs)
        assocs = set(map(mapping.USER_FIELD.get_uuid, assocs))
        uuid_filters.append(partial(contains, assocs))

    async def get_full_employee(*args, **kwargs):
        return await get_one_employee(
            *args,
            **kwargs,
            details=EmployeeDetails.FULL,
            only_primary_uuid=only_primary_uuid
        )

    search_result = await c.bruger.paged_get(
        get_full_employee, uuid_filters=uuid_filters, **kwargs
    )
    return search_result


@router.post("/e/{uuid}/terminate")
# @util.restrictargs('force', 'triggerless')
async def terminate_employee(
    uuid: UUID, request: dict = Body(...), permissions=Depends(oidc.rbac_owner)
):
    """Terminates an employee and all of his roles beginning at a
    specified date. Except for the manager roles, which we vacate
    instead.

    .. :quickref: Employee; Terminate

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: The termination succeeded.

    :param uuid: The UUID of the employee to be terminated.

    :<json string to: When the termination should occur, as an ISO 8601 date.
    :<json boolean vacate: *Optional* - mark applicable — currently
        only ``manager`` -- functions as _vacant_, i.e. simply detach
        the employee from them.

    **Example Request**:

    .. sourcecode:: json

      {
        "validity": {
          "to": "2015-12-31"
        }
      }

    """
    uuid = str(uuid)
    date = util.get_valid_to(request)

    c = lora.Connector(effective_date=date, virkningtil="infinity")

    request_handlers = [
        await handlers.get_handler_for_function(obj).construct(
            {
                "uuid": objid,
                "vacate": util.checked_get(request, "vacate", False),
                "validity": {
                    "to": util.to_iso_date(
                        # we also want to handle _future_ relations
                        max(date, min(map(util.get_effect_from, util.get_states(obj)))),
                        is_end=True,
                    ),
                },
            },
            mapping.RequestType.TERMINATE,
        )
        for objid, obj in await c.organisationfunktion.get_all(
            tilknyttedebrugere=uuid,
            gyldighed="Aktiv",
        )
    ]

    trigger_dict = {
        Trigger.ROLE_TYPE: mapping.EMPLOYEE,
        Trigger.EVENT_TYPE: mapping.EventType.ON_BEFORE,
        Trigger.REQUEST: request,
        Trigger.REQUEST_TYPE: mapping.RequestType.TERMINATE,
        Trigger.EMPLOYEE_UUID: uuid,
        Trigger.UUID: uuid,
    }

    if not util.get_args_flag("triggerless"):
        await Trigger.run(trigger_dict)

    for handler in request_handlers:
        await handler.submit()

    result = uuid

    trigger_dict[Trigger.EVENT_TYPE] = mapping.EventType.ON_AFTER
    trigger_dict[Trigger.RESULT] = result

    if not util.get_args_flag("triggerless"):
        await Trigger.run(trigger_dict)

    # Write a noop entry to the user, to be used for the history
    await common.add_history_entry(c.bruger, uuid, "Afslut medarbejder")

    return result


# When RBAC enabled: currently, only the admin role can create employees
@router.post("/e/create", status_code=201)
async def create_employee(req: dict = Body(...), permissions=Depends(oidc.rbac_admin)):
    """Create a new employee

    .. :quickref: Employee; Create

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: Creation succeeded.

    **Example Request**:

    :<json string name: Name of the employee.
    :<json string givenname: Given name of the employee.
    :<json string surname: Surname of the employee.
    :<json string nickname: Nickname of the employee.
    :<json string nickname_givenname: The given name part of the nickname.
    :<json string nickname_surname: The surname part of the nickname.
    :<json string cpr_no: The CPR no of the employee
    :<json string user_key: Short, unique key identifying the employee.
    :<json object org: The organisation with which the employee is associated
    :<json string uuid: An **optional** parameter, that will be used as the
      UUID for the employee.
    :<json list details: A list of details to be created for the employee.

    For both the name and the nickname, only the full name or
    givenname/surname should be given, not both.
    If only the full name is supplied, the name will be split on the last
    space.

    For more information on the available details,
    see: http:post:`/service/details/create`.
    Note, that the ``person`` parameter is implicit in these payload, and
    should not be given.

    .. sourcecode:: json

      {
        "name": "Name Name",
        "nickname": "Nickname Whatever",
        "cpr_no": "0101501234",
        "user_key": "1234",
        "org": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f",
        "details": [
          {
            "type": "engagement",
            "org_unit": {
              "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
            },
            "job_function": {
              "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
            },
            "engagement_type": {
              "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
            },
            "validity": {
                "from": "2016-01-01",
                "to": "2017-12-31"
            }
          }
        ]
      }

    :returns: UUID of created employee

    """
    request = await EmployeeRequestHandler.construct(req, mapping.RequestType.CREATE)
    return await request.submit()


def _inject_persons(details, employee_uuid, valid_from, valid_to):
    decorated = copy.deepcopy(details)
    for detail in decorated:
        detail["person"] = {
            mapping.UUID: employee_uuid,
            mapping.VALID_FROM: valid_from,
            mapping.VALID_TO: valid_to,
            "allow_nonexistent": True,
        }

    return decorated

#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import operator
import os
import requests
import traceback
import uuid

import flask

from . import cli
from . import lora
from . import util
from .converters import addr
from .converters import reading
from .converters import writing

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')

cli.load_cli(app)


@app.errorhandler(ValueError)
def handle_invalid_usage(error):
    msg = '\n'.join(error.args)
    flask.current_app.logger.exception(msg)
    return msg, 400


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    stack = traceback.format_exc()
    flask.current_app.logger.exception('AN ERROR OCCURRED')

    return (
        flask.render_template('error.html', stack=stack, now=util.now()),
        500,
    )


@app.route('/')
def root():
    return flask.send_from_directory(staticdir, 'index.html')


@app.route('/scripts/<path:path>')
def send_scripts(path):
    return flask.send_from_directory(staticdir, os.path.join('scripts', path))


@app.route('/styles/<path:path>')
def send_styles(path):
    return flask.send_from_directory(staticdir, os.path.join('styles', path))


@app.route('/service/user/<user>/login', methods=['POST'])
def login(user):
    r = lora.login(user, flask.request.get_json()['password'])

    if r:
        return flask.jsonify(r)
    else:
        return '', 401


@app.route('/service/user/<user>/logout', methods=['POST'])
def logout(user):
    return flask.jsonify(
        lora.logout(user, flask.request.headers['X-AUTH-TOKEN'])
    )


@app.route('/acl/', methods=['POST', 'GET'])
def acl():
    return flask.jsonify([])


@app.route('/o/')
def list_organisations():
    return flask.jsonify(reading.list_organisations())


# --- Writing to LoRa --- #


@app.route('/o/<uuid:orgid>/org-unit', methods=['POST'])
def create_organisation_unit(orgid):
    req = flask.request.get_json()
    org_unit = writing.create_org_unit(req)
    uuid = lora.create('organisation/organisationenhed', org_unit)

    # If an end date is set for the org unit, inactivate it automatically
    # from this date
    if 'valid-to' in req:
        org_unit = writing.inactivate_org_unit(req['valid-to'])
        lora.update('organisation/organisationenhed/%s' % uuid, org_unit)

    return flask.jsonify({'uuid': uuid}), 201


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['DELETE'])
@util.restrictargs('endDate')
def inactivate_org_unit(orgid, unitid):
    payload = writing.inactivate_org_unit(flask.request.args.get('endDate'))
    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/actions/move',
           methods=['POST'])
@util.restrictargs()
def move_org_unit(orgid, unitid):
    # TODO: refactor common behavior from this route and the one below

    req = flask.request.get_json()
    payload = writing.move_org_unit(req)

    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>', methods=['POST'])
@util.restrictargs('rename')
def rename_or_retype_org_unit(orgid, unitid):
    rename = flask.request.args.get('rename', None)

    req = flask.request.get_json()

    if rename:
        # Renaming an org unit
        payload = writing.rename_org_unit(req)
    else:
        # Changing the org units enhedstype
        assert req['type']
        payload = writing.retype_org_unit(req)

    lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location',
    methods=['POST'],
)
@app.route(
    '/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/location/<uuid:roleid>',
    methods=['POST'],
)
def update_organisation_unit_location(orgid, unitid, roleid=None):
    # TODO: write test for this

    req = flask.request.get_json()
    roletype = req.get('role-type')

    kwargs = writing.create_update_kwargs(roletype, req)
    payload = writing.update_org_unit_addresses(
        unitid, roletype, **kwargs)

    if payload['relationer']['adresser']:
        lora.update('organisation/organisationenhed/%s' % unitid, payload)

    return flask.jsonify({'uuid': unitid}), 200


@app.route('/o/<uuid:orgid>/full-hierarchy')
@util.restrictargs('treeType', 'orgUnitId', 'query',
                   'effective-date', 't')
def full_hierarchy(orgid):
    args = flask.request.args

    params = dict(
        effective_date=args.get('effective-date', None),
        include_children=True,
    )

    if args.get('query'):
        # TODO: the query argument does sub-tree searching -- given
        # that LoRA has no notion of the organisation tree, we'd have
        # to emulate it
        flask.current_app.logger.error('sub-tree searching is unsupported!')
        return '', 400

    if args.get('treeType', None) == 'specific':
        r = reading.full_hierarchy(str(orgid), args['orgUnitId'], **params)

        if r:
            return flask.jsonify(
                r['children'],
            )
        else:
            return '', 404

    else:
        r = reading.full_hierarchies(str(orgid), str(orgid), **params)

        if r:
            return flask.jsonify(reading.wrap_in_org(str(orgid), r[0]))
        else:
            return '', 404


@app.route('/o/<uuid:orgid>/org-unit/')
@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/')
@util.restrictargs('query', 'validity', 'effective-date', 'limit', 'start',
                   't')
def get_orgunit(orgid, unitid=None):

    # TODO: we are not actually using the 't' parameter - we should
    # probably remove this from the frontend calls later on...

    query = flask.request.args.get('query', None)
    params = {
        'tilhoerer': str(orgid),
    }

    if query:
        assert unitid is None, 'unitid and query are both set!'

        try:
            params['uuid'] = str(uuid.UUID(query))
        except ValueError:
            # If the query is not an UUID, search for an org unit name instead
            params['enhedsnavn'] = query
    else:
        params['uuid'] = unitid

    params.update(
        effective_date=flask.request.args.get('effective-date', None),
    )

    r = list(filter(None, (
        reading.full_hierarchy(
            str(orgid), orgunitid,
            include_children=False, include_parents=True,
            include_activename=True,
            effective_date=flask.request.args.get('effective-date', None),
            validity=flask.request.args.get('validity', None),
        )
        for orgunitid in lora.organisationenhed(**params)
    )))

    return flask.jsonify(r) if r else ('', 404)


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/history/')
@util.restrictargs()
def get_orgunit_history(orgid, unitid):
    r = reading.unit_history(str(orgid), str(unitid))

    return flask.jsonify(list(r)) if r else ('', 404)


@app.route('/o/<uuid:orgid>/org-unit/<uuid:unitid>/role-types/<role>/')
def get_role(orgid, unitid, role):
    if role not in ['contact-channel', 'location']:
        return flask.jsonify([]), 400

    validity = flask.request.args.get('validity')

    getters = {
        'contact-channel': reading.get_contact_channel,
        'location': reading.get_location,
    }

    if role not in getters:
        flask.current_app.logger.warn('unsupported role {!r}'.format(role))
        return flask.jsonify([]), 400

    r = getters[role](unitid, validity=validity)

    if r:
        return flask.jsonify(r)
    else:
        return '', 404


#
# Classification stuff - should be moved to own file
#

# This one is used when creating new "Enheder"
@app.route('/org-unit/type')
def list_classes():
    return flask.jsonify(reading.get_classes())


@app.route('/addressws/geographical-location')
@util.restrictargs('local', required=['vejnavn'])
def get_geographical_addresses():
    return flask.jsonify(
        addr.autocomplete_address(flask.request.args['vejnavn'],
                                  flask.request.args.get('local')),
    )


@app.route('/role-types/contact/facets/properties/classes/')
def get_contact_facet_properties_classes():
    # This yields three options in the original Mock test:
    # internal-only, external and unlisted. (In Danish: “Må vises
    # internt”, “Må vises eksternt” and “Hemmligt”.)
    return flask.jsonify([
        {
            "name": "N/A",
            "user-key": "N/A",
            "uuid": "00000000-0000-0000-0000-000000000000"
        },
    ])


@app.route('/role-types/contact/facets/type/classes/')
def get_contact_facet_types_classes():
    key = flask.request.args.get('facetKey')
    assert key == 'Contact_channel_location', 'unknown key: ' + key

    return flask.jsonify([
        {
            "name": "Phone Number",
            "prefix": "urn:magenta.dk:telefon:",
            "uuid": "b7ccfb21-f623-4e8f-80ce-89731f726224"
        },
    ])

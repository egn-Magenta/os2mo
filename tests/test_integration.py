#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
import requests

from mora import lora
from mora import settings

from . import util


class IntegrationTests(util.LoRATestCase):
    maxDiff = None

    def test_sanity(self):
        r = requests.get(self.lora_url)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_empty(self):
        r = requests.get(self.lora_url)
        self.assertTrue(r.ok)
        self.assertEqual(r.json().keys(), {'site-map'})

    def test_list_classes(self):
        self.load_sample_structures()

        self.assertEqual(
            [
                {
                    'name': 'Afdeling',
                    'userKey': 'afd',
                    'user-key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                {
                    'name': 'Fakultet',
                    'userKey': 'fak',
                    'user-key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                {
                    'name': 'Institut',
                    'userKey': 'inst',
                    'user-key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                }
            ],
            self.client.get('/org-unit/type').json,
        )

    def test_organisation(self):
        'Test getting the organisation'

        self.assertRequestResponse('/o/', [])

        r = self.client.get('/o/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, [])

        self.load_sample_structures()

        self.assertRequestResponse('/o/', [
            {
                'hierarchy': {
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'children': [],
                    'name': 'Overordnet Enhed',
                    'hasChildren': True,
                    'valid-to': 'infinity',
                    'valid-from': '01-01-2016',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                },
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'valid-to': 'infinity',
                'valid-from': '01-01-2016',
            },
        ])

    def test_organisation_empty(self):
        'Handle no organisations'
        self.assertRequestResponse('/o/', [])

    def test_hierarchies(self):
        'Test the full-hierarchy listing'

        # then inject an organisation and find it
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy'
            '?treeType=treeType',
            {
                'hierarchy': {
                    'children': [
                        {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Humanistisk fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'type': {
                                'name': 'Institut',
                                'userKey': 'inst',
                                'user-key': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                            'user-key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'type': {
                                'name': 'Fakultet',
                                'userKey': 'fak',
                                'user-key': 'fak',
                                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                            },
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '01-01-2017',
                            'valid-to': 'infinity'
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '01-01-2016',
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '01-01-2016',
                'valid-to': 'infinity',
            })

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy',
            {
                'hierarchy': {
                    'children': [
                        {
                            'children': [],
                            'hasChildren': True,
                            'name': 'Humanistisk fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'hum',
                            'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'valid-from': '01-01-2016',
                            'valid-to': 'infinity',
                            'type': {
                                'name': 'Institut',
                                'userKey': 'inst',
                                'user-key': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                        },
                        {
                            'children': [],
                            'hasChildren': False,
                            'name': 'Samfundsvidenskabelige fakultet',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                            'user-key': 'samf',
                            'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                            'valid-from': '01-01-2017',
                            'valid-to': 'infinity',
                            'type': {
                                'name': 'Fakultet',
                                'userKey': 'fak',
                                'user-key': 'fak',
                                'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                            },
                        },
                    ],
                    'hasChildren': True,
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '01-01-2016',
                    'type': {
                        'name': 'Afdeling',
                        'user-key': 'afd',
                        'userKey': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'valid-to': 'infinity'},
                'name': 'Aarhus Universitet',
                'user-key': 'AU',
                'uuid': '456362c4-0ee4-4e5e-a72c-751239745e62',
                'valid-from': '01-01-2016',
                'valid-to': 'infinity',
            })

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/full-hierarchy?'
            'treeType=specific&orgUnitId=2874e1dc-85e6-4269-823a-e1125484dfd3',
            [
                {
                    'children': [],
                    'hasChildren': True,
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
                {
                    'children': [],
                    'hasChildren': False,
                    'name': 'Samfundsvidenskabelige fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'type': {
                        'name': 'Fakultet',
                        'user-key': 'fak',
                        'userKey': 'fak',
                        'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                    },
                    'user-key': 'samf',
                    'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0',
                    'valid-from': '01-01-2017',
                    'valid-to': 'infinity',
                }
            ]
        )

    @freezegun.freeze_time('2017-06-01')
    def test_org_units(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e/',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': {
                        'activeName': 'Overordnet Enhed',
                        'name': 'Overordnet Enhed',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': None,
                        'parent-object': None,
                        'user-key': 'root',
                        'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                        'valid-from': '01-01-2016',
                        'valid-to': 'infinity',
                        'type': {
                            'name': 'Afdeling',
                            'userKey': 'afd',
                            'user-key': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                    },
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                }
            ]
        )

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '?query=Hum%',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': None,
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                }
            ]
        )
        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '?query=9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
            [
                {
                    'activeName': 'Humanistisk fakultet',
                    'name': 'Humanistisk fakultet',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'parent-object': None,
                    'user-key': 'hum',
                    'uuid': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                    'type': {
                        'name': 'Institut',
                        'user-key': 'inst',
                        'userKey': 'inst',
                        'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                    },
                }
            ]
        )

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
            '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3'
            '/role-types/location/?validity=present',
            [
                {
                    'location': {
                        'name': 'Kontor',
                        'vejnavn': 'Nordre Ringgade 1, 8000 Aarhus C',
                        'user-key': '07515902___1_______',
                        'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                        'valid-from': '2014-05-05T19:07:48.577000+00:00',
                        'valid-to': 'infinity',
                    },
                    'name': 'Kontor',
                    'org-unit': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'primaer': True,
                    'role-type': 'location',
                    'user-key': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'uuid': 'b1f1817d-5f02-4331-b8b3-97330a5d3197',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

        with self.subTest('invalid validity'):
            self.assert400(self.client.get(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/2874e1dc-85e6-4269-823a-e1125484dfd3/'
                '?validity=kaflaflibob',
            ))

    @freezegun.freeze_time('2017-06-01')
    def test_org_unit_temporality(self):
        self.load_sample_structures()

        with self.subTest('past'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=past',
                [
                    {
                        'activeName': 'Afdeling for Fremtidshistorik',
                        'name': 'Afdeling for Fremtidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': None,
                            'type': {
                                'name': 'Institut',
                                'userKey': 'inst',
                                'user-key': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': '01-01-2019',
                        },
                        'type': {
                            'name': 'Afdeling',
                            'userKey': 'afd',
                            'user-key': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2016',
                        'valid-to': '01-01-2017',
                    },
                ],
            )

        with self.subTest('empty past'):
            self.assert404(
                self.client.get(
                    '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                    '/org-unit/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                    '/role-types/contact-channel/?validity=past'
                )
            )

        with self.subTest('present'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=present',
                [
                    {
                        'activeName': 'Afdeling for Samtidshistorik',
                        'name': 'Afdeling for Samtidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': None,
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': '01-01-2019',
                            'type': {
                                'name': 'Institut',
                                'userKey': 'inst',
                                'user-key': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2017',
                        'valid-to': '01-01-2018',
                        'type': {
                            'name': 'Afdeling',
                            'userKey': 'afd',
                            'user-key': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                    },
                ],
            )

        with self.subTest('future'):
            self.assertRequestResponse(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
                '04c78fc2-72d2-4d02-b55f-807af19eac48/?validity=future',
                [
                    {
                        'activeName': 'Afdeling for Fortidshistorik',
                        'name': 'Afdeling for Fortidshistorik',
                        'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                        'parent': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                        'parent-object': {
                            'activeName': 'Historisk Institut',
                            'name': 'Historisk Institut',
                            'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                            'parent': '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',
                            'parent-object': None,
                            'user-key': 'hist',
                            'uuid': 'da77153e-30f3-4dc2-a611-ee912a28d8aa',
                            'valid-from': '01-01-2016',
                            'valid-to': '01-01-2019',
                            'type': {
                                'name': 'Institut',
                                'userKey': 'inst',
                                'user-key': 'inst',
                                'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                            },
                        },
                        'type': {
                            'name': 'Afdeling',
                            'userKey': 'afd',
                            'user-key': 'afd',
                            'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                        },
                        'user-key': 'frem',
                        'uuid': '04c78fc2-72d2-4d02-b55f-807af19eac48',
                        'valid-from': '01-01-2018',
                        'valid-to': '01-01-2019',
                    },
                ],
            )

        with self.subTest('empty future'):
            self.assertRequestFails(
                '/o/456362c4-0ee4-4e5e-a72c-751239745e62'
                '/org-unit/9d07123e-47ac-4a9a-88c8-da82e3a4bc9e'
                '/role-types/contact-channel/?validity=future',
                404,
            )

    def test_should_add_one_new_contact_channel_correctly(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            'b688513d-11f7-4efc-b679-ab082a2055d0/role-types/location/'
            '00000000-0000-0000-0000-000000000000',
            {'uuid': 'b688513d-11f7-4efc-b679-ab082a2055d0'},
            json=util.get_mock_data(
                'mo/writing/update_org_unit_contact_channel.json',
            )
        )

        # TODO: This test should also ask for the values from LoRa

    def test_effective_date_with_plus(self):
        self.load_sample_structures(minimal=True)

        self.assertRequestResponse(
            '/o/456362c4-0ee4-4e5e-a72c-751239745e62/org-unit/'
            '?query=2874e1dc-85e6-4269-823a-e1125484dfd3'
            '&effective-date=2017-07-31T22:00:00+00:00',
            [
                {
                    'activeName': 'Overordnet Enhed',
                    'name': 'Overordnet Enhed',
                    'org': '456362c4-0ee4-4e5e-a72c-751239745e62',
                    'parent': None,
                    'parent-object': None,
                    'type': {
                        'name': 'Afdeling',
                        'userKey': 'afd',
                        'user-key': 'afd',
                        'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                    },
                    'user-key': 'root',
                    'uuid': '2874e1dc-85e6-4269-823a-e1125484dfd3',
                    'valid-from': '01-01-2016',
                    'valid-to': 'infinity',
                },
            ],
        )

    def test_history_for_org_unit(self):
        self.load_sample_structures()

        ORG = '456362c4-0ee4-4e5e-a72c-751239745e62'
        SAMF_UNIT = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        # Expire the unit in order to get some more data in the history log
        self.assertRequestResponse(
            '/o/%s/org-unit/%s?endDate=01-01-2018' % (ORG, SAMF_UNIT),
            {
                'uuid': SAMF_UNIT,
            },
            method='DELETE',
        )

        # Easier than using self.assertRequestResponse due to timestamps
        r = self.client.get(
            '/o/%s/org-unit/%s/history/?t=notUsed' % (ORG, SAMF_UNIT)
        )

        # TODO: check more than just the status code
        self.assertEqual(200, r.status_code)

    def test_verify_relation_names(self):
        '''Verify that our list of relation names is correct.'''
        attrs = set()
        rels = set()

        def get(p):
            r = lora.session.get(settings.LORA_URL.rstrip('/') + p)
            r.raise_for_status()
            return r.json()

        for rule in get('/site-map')['site-map']:
            if rule.endswith('fields'):
                r = get(rule)

                attrs.update(r['attributter']['egenskaber'])
                rels.update(r['relationer_nul_til_en'])
                rels.update(r['relationer_nul_til_mange'])

        # I wish relation and attribute names were disjoint :(
        self.assertEqual(rels & attrs, {'interessefaellesskabstype'})

        rels -= {'interessefaellesskabstype'}

        self.assertEqual(rels, lora.ALL_RELATION_NAMES)

    def test_list_orgunit_classes(self):
        self.load_sample_structures()

        self.assertRequestResponse(
            '/org-unit/type',
            [
                {
                    'name': 'Afdeling',
                    'userKey': 'afd',
                    'user-key': 'afd',
                    'uuid': '32547559-cfc1-4d97-94c6-70b192eff825',
                },
                {
                    'name': 'Fakultet',
                    'userKey': 'fak',
                    'user-key': 'fak',
                    'uuid': '4311e351-6a3c-4e7e-ae60-8a3b2938fbd6',
                },
                {
                    'name': 'Institut',
                    'userKey': 'inst',
                    'user-key': 'inst',
                    'uuid': 'ca76a441-6226-404f-88a9-31e02e420e52',
                },
            ],
        )

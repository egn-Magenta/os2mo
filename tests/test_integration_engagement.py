#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun

from mora import lora
from tests import util


@freezegun.freeze_time('2017-01-01', tz_offset=1)
class Tests(util.LoRATestCase):
    maxDiff = None

    def test_create_engagement(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "engagement",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                }
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Engagement",
                        "funktionsnavn": "Engagement"
                    }
                ]
            }
        }

        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 1)
        engagementid = engagements[0]

        actual_engagement = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(actual_engagement, expected)

    def test_create_engagement_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "engagement",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {
                    'uuid': "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"
                },
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                }
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "opgaver": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "infinity",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Engagement",
                        "funktionsnavn": "Engagement"
                    }
                ]
            }
        }

        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 1)
        engagementid = engagements[0]

        actual_engagement = c.organisationfunktion.get(engagementid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(actual_engagement, expected)

    def test_create_engagement_no_job_function(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "6ee24785-ee9a-4502-81c2-7697009c9053"

        payload = [
            {
                "type": "engagement",
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "engagement_type": {
                    'uuid': "62ec821f-4179-4758-bfdf-134529d186e9"},
                "validity": {
                    "from": "2017-12-01T00:00:00+01",
                    "to": "2017-12-02T00:00:00+01",
                }
            }
        ]

        self.assertRequestResponse('/service/e/{}/create'.format(userid),
                                   userid, json=payload)

        expected = {
            "livscykluskode": "Opstaaet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "gyldighed": "Aktiv"
                    }
                ]
            },
            "note": "Oprettet i MO",
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
                    }
                ],
                "tilknyttedebrugere": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "6ee24785-ee9a-4502-81c2-7697009c9053"
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "to_included": False,
                            "to": "2017-12-02 00:00:00+01",
                            "from_included": True,
                            "from": "2017-12-01 00:00:00+01"
                        },
                        "brugervendtnoegle": "6ee24785-ee9a-4502-81c2-"
                                             "7697009c9053 9d07123e-"
                                             "47ac-4a9a-88c8-da82e3a4bc9e "
                                             "Engagement",
                        "funktionsnavn": "Engagement"
                    }
                ]
            }
        }

        engagements = c.organisationfunktion.fetch(tilknyttedebrugere=userid)
        self.assertEqual(len(engagements), 1)
        engagementid = engagements[0]

        actual_engagement = c.organisationfunktion.get(engagementid)

        self.assertRegistrationsEqual(expected, actual_engagement)

    def test_create_engagement_fails_on_empty_payload(self):
        self.load_sample_structures()

        payload = [
            {
                "type": "engagement",
            }
        ]

        self.assertRequestFails(
            '/service/e/6ee24785-ee9a-4502-81c2-7697009c9053/create', 400,
            json=payload)

    def test_edit_engagement_no_overwrite(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'

        req = [{
            "type": "engagement",
            "uuid": engagement_uuid,
            "data": {
                "job_function": {
                    'uuid': "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                "engagement_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"
                },
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                }
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }

                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_engagement = c.organisationfunktion.get(engagement_uuid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(expected_engagement, actual_engagement)

    def test_edit_engagement_overwrite(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'

        req = [{
            "type": "engagement",
            "uuid": engagement_uuid,
            "original": {
                "validity": {
                    "from": "2017-01-01 00:00:00+01",
                    "to": None,
                },
                "org_unit": {'uuid': "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"},
                "job_function": {
                    'uuid': "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"},
                "engagement_type": {
                    'uuid': "32547559-cfc1-4d97-94c6-70b192eff825"},
            },
            "data": {
                "job_function": {
                    'uuid': "cac9c6a8-b432-4e50-b33e-e96f742d4d56"},
                "engagement_type": {
                    'uuid': "bcd05828-cc10-48b1-bc48-2f0d204859b2"},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                }
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "cac9c6a8-b432-4e50-b33e-e96f742d4d56",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }

                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "bcd05828-cc10-48b1-bc48-2f0d204859b2",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_engagement = c.organisationfunktion.get(engagement_uuid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(expected_engagement, actual_engagement)

    def test_edit_engagement_move(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'

        req = [{
            "type": "engagement",
            "uuid": engagement_uuid,
            "data": {
                "org_unit": {'uuid': "b688513d-11f7-4efc-b679-ab082a2055d0"},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                    "to": "2019-04-01T00:00:00+02",
                },
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2019-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "2019-04-01 00:00:00+02"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "2019-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2019-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_engagement = c.organisationfunktion.get(engagement_uuid)

        self.assertRegistrationsEqual(expected_engagement, actual_engagement)

    def test_edit_engagement_move_no_valid_to(self):
        self.load_sample_structures()

        # Check the POST request
        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'

        req = [{
            "type": "engagement",
            "uuid": engagement_uuid,
            "data": {
                "org_unit": {'uuid': "b688513d-11f7-4efc-b679-ab082a2055d0"},
                "validity": {
                    "from": "2018-04-01T00:00:00+02",
                }
            },
        }]

        self.assertRequestResponse(
            '/service/e/{}/edit'.format(userid),
            userid, json=req)

        expected_engagement = {
            "note": "Rediger engagement",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    },
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        },
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2018-04-01 00:00:00+02"
                        }
                    },
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2018-04-01 00:00:00+02",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement"
                    }
                ]
            },
        }

        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        actual_engagement = c.organisationfunktion.get(engagement_uuid)

        self.assertRegistrationsEqual(expected_engagement, actual_engagement)

    def test_terminate_engagement(self):
        self.load_sample_structures()

        # Check the POST request
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

        userid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"

        payload = {
            "validity": {
                "from": "2017-12-01T00:00:00+01"
            }
        }

        self.assertRequestResponse('/service/e/{}/terminate'.format(userid),
                                   userid, json=payload)

        expected = {
            "note": "Afslut medarbejder",
            "relationer": {
                "opgaver": [
                    {
                        "uuid": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "organisatoriskfunktionstype": [
                    {
                        "uuid": "32547559-cfc1-4d97-94c6-70b192eff825",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeorganisationer": [
                    {
                        "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ],
                "tilknyttedeenheder": [
                    {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ],
                "tilknyttedebrugere": [
                    {
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        }
                    }
                ]
            },
            "livscykluskode": "Rettet",
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "2017-12-01 00:00:00+01"
                        }
                    },
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-12-01 00:00:00+01",
                            "to": "infinity"
                        }
                    },
                ]
            },
            "attributter": {
                "organisationfunktionegenskaber": [
                    {
                        "virkning": {
                            "from_included": True,
                            "to_included": False,
                            "from": "2017-01-01 00:00:00+01",
                            "to": "infinity"
                        },
                        "brugervendtnoegle": "bvn",
                        "funktionsnavn": "Engagement"
                    }
                ]
            },
        }

        engagement_uuid = 'd000591f-8705-4324-897a-075e3623f37b'

        actual_engagement = c.organisationfunktion.get(engagement_uuid)

        # drop lora-generated timestamps & users
        del actual_engagement['fratidspunkt'], actual_engagement[
            'tiltidspunkt'], actual_engagement[
            'brugerref']

        self.assertEqual(actual_engagement, expected)

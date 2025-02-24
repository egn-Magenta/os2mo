CHANGELOG
=========

3.34.0 - 2022-02-22
-------------------

[#48786] Fix version

3.33.2 - 2022-02-21
-------------------

[#48745] Utilize new config-updater

3.33.1 - 2022-02-21
-------------------

[#42981] Fixup broken CI release stage and dev environment

3.33.0 - 2022-02-19
-------------------

[#42981] Split the MO backend and frontend into seperate containers

Two seperate containers must now be started in order to launch MO with UI.

3.32.1 - 2022-02-16
-------------------

[#47844] Parse Base64 auth UUID as little endian bytes, as that is what is sent
to us from ADFS

3.32.0 - 2022-02-15
-------------------

[#48553] Add support for Keycloak Base64 encoded UUID attribute

The ObjectGUID LDAP attribute sent from ADFS to Keycloak, is sent as a Base64
encoded byte-string. There is no easy way to perform conversion of this in
either ADFS or Keycloak, so we add additional support for this eventuality in
our KeycloakToken.

3.31.0 - 2022-02-11
-------------------

[#48565] Pluralise KLE Aspects

3.30.5 - 2022-02-09
-------------------

[#42981] Test new docker-release template

3.30.4 - 2022-02-07
-------------------

[#47514] Rename default Keycloak client name to 'mo-frontend'

3.30.3 - 2022-02-03
-------------------

[#48177] Rearrange GraphAPI code, fix typing

3.30.2 - 2022-02-02
-------------------

[#48307] Fix and type dataloaders, check Nones

3.30.1 - 2022-02-01
-------------------

[#48176] Use models from RAModels

3.30.0 - 2022-02-01
-------------------

[#47789] Add manager inheritance for organisation units

3.29.13 - 2022-01-28
--------------------

[#47788] Add filtering of addresses per address type

3.29.12 - 2022-01-24
--------------------

[#48042] GraphQL: make reference to org_unit's plural for RelatedUnits

3.29.11 - 2022-01-21
--------------------

[#48003] Fix bug in dataset health endpoint

3.29.10 - 2022-01-20
--------------------

[#48074] Turn off GraphiQL in production

3.29.9 - 2022-01-19
-------------------

[#48039] Fix double event loop for real

3.29.8 - 2022-01-19
-------------------

[#47851] Make health output optionally null

3.29.7 - 2022-01-19
-------------------

[#48039] Fix double event loop

3.29.6 - 2022-01-18
-------------------

[#47969] Update docstrings in GraphAPI related files

3.29.5 - 2022-01-17
-------------------

[#47770] Test of GraphQL class and facet reading

3.29.4 - 2022-01-17
-------------------

[#48000] Test of GraphQL ITSystem reading

3.29.3 - 2022-01-17
-------------------

[#47985] Remove trailing Type from GraphQL models

3.29.2 - 2022-01-14
-------------------

[#47961] Fix UI trailing slash issues

3.29.1 - 2022-01-14
-------------------

[#47761] Test the GraphAPI for details read

3.29.0 - 2022-01-14
-------------------

[#47761] Rename GraphQL endpoints to plural

3.28.0 - 2022-01-13
-------------------

[#47918] Shim out itsystem endpoints

3.27.0 - 2022-01-13
-------------------

[#47916] Convert healthchecks to GraphQL

3.26.0 - 2022-01-13
-------------------

[#47915] Shim out version endpoint

3.25.0 - 2022-01-13
-------------------

[#47674] Removed integrationdata endpoint

3.24.0 - 2022-01-12
-------------------

[#47751] Kubernetes liveness and readiness probe

3.23.7 - 2022-01-11
-------------------

[#47680] Update dependencies

3.23.6 - 2022-01-10
-------------------

[#47680] Remove validity from Klasser and Facetter in the GraphQL API

3.23.5 - 2022-01-05
-------------------

[#47784] Temporarily remove heavy metrics

We have discovered that metrics are being updated on EVERY REQUEST against MO!
Not just on requests against the /metrics endpoint, as we had imagined.

This means that every single request against MO results in 5 requests to other systems.
Among these is a request to DAR, which means that MOs minimum request response-time is the round-trip time to DAR.

This change temporarily disables these 5 metrics, with a plan to reintroduce them later.

3.23.4 - 2022-01-05
-------------------

[#47759] Fix person_uuid -> employee_uuid in ReadingHandlers for GraphQL

3.23.3 - 2022-01-05
-------------------

[#47699] Use employee consistently instead of mixing person and employee

3.23.2 - 2022-01-05
-------------------

[#47681] Remove imports from impl for GraphQL

3.23.1 - 2022-01-05
-------------------

[#47742] Update translation of two files.

3.23.0 - 2022-01-05
-------------------

[#47101] Connect details to organisational units with GraphQL

3.22.0 - 2022-01-04
-------------------

[#47652] Add option to show GIR logo instead of OS2MO

3.21.0 - 2022-01-03
-------------------

[#44717] Added confdb metric to ease removal

3.20.0 - 2021-12-22
-------------------

[#47101] Connect org_units to details using GraphQL

3.19.0 - 2021-12-22
-------------------

[#47101] Connect details to Employee with GraphQL

3.18.3 - 2021-12-21
-------------------

[#47101] Connect Employee to details with GraphQL

3.18.2 - 2021-12-21
-------------------

Fix check of UUIDs in GraphQL reads

3.18.1 - 2021-12-21
-------------------

[#47640] Only load unique UUIDs in main GraphQL schema

3.18.0 - 2021-12-20
-------------------

[#47090] Initial work on facets in GraphQL

3.17.1 - 2021-12-18
-------------------

[#47608] Initial work on new release cadence

3.17.0 - 2021-12-17
-------------------

[#47099] Implement GraphQL reading of RelatedUnits

3.16.0 - 2021-12-17
-------------------

[#47090] Initial work on class GraphQL

3.15.1 - 2021-12-17
-------------------

[#45051] Remove DAR multiloop dataloader workaround

3.15.0 - 2021-12-17
-------------------

[#7100] Implement Role- and ITUser reading in GraphQL

3.14.0 - 2021-12-17
-------------------

[#47093] Implement Association reading in graphQL

3.13.0 - 2021-12-17
-------------------

[#47097] Implement Leave reading in GraphQL

3.12.0 - 2021-12-17
-------------------

[#47091] Implement address reading in GraphQL

3.11.0 - 2021-12-17
-------------------

[#47096] Implement KLE reading in GraphQL

3.10.0 - 2021-12-16
-------------------

[#47094] Allow read of engagements through GraphQL

3.9.4 - 2021-12-16
------------------

[#47594] Delete sync requests, use async httpx

3.9.3 - 2021-12-16
------------------

[#46544] Share AMQP connection pools

3.9.2 - 2021-12-08
------------------

[#46388] Changes misleading link description

3.9.1 - 2021-12-03
------------------

[#47388] Remove GraphQL auth classes

3.9.0 - 2021-12-03
------------------

[#47415] Update Organisation GraphQL implementation to use datamodel from `ramodels`

3.8.4 - 2021-12-03
------------------

[#47196] Revert auth changes

3.8.3 - 2021-12-02
------------------

[#47386] Implement Gitlab CI templates

3.8.2 - 2021-12-01
------------------

[#47088] Update Employee GraphQL read implementation

3.8.1 - 2021-12-01
------------------

[#47196] Fix auth check on configuration endpoints

3.8.0 - 2021-12-01
------------------

[#47360] Add possibility of returning flat objects from ReadingHandler'

3.7.1 - 2021-12-01
------------------

[#47196] Support generating the Keycloak hostname dynamically based on where OS2mo is deployed

This can be controlled via a new configuration value `CONFDB_DYNAMIC_KEYCLOAK_URL`

3.7.0 - 2021-12-01
------------------

[#46388] Added download insights as CSV to the frontend

3.6.2 - 2021-11-30
------------------

Parse seniority as Optional[datetime]. Return None if applicable in read

3.6.1 - 2021-11-29
------------------

[#47087] Update OrganisationUnit GraphQL implementation

3.6.0 - 2021-11-24
------------------

[#47144] Add `cpr_validate_birthdate` feature flag which can disable the default validation of CPR birthdates

3.5.1 - 2021-11-24
------------------

[#43398] Fix legacy auth support supporting too few concurrent SQLalchemy connections

3.5.0 - 2021-11-23
------------------

[#46388] Added download insights as CSV endpoint

3.4.9 - 2021-11-22
------------------

[#47086] Switch from ASGI to FastAPI integration

3.4.8 - 2021-11-15
------------------

[#46937] Fixed GraphQL auth bug

3.4.7 - 2021-11-04
------------------

[#xxxxx] Ensure FluxCD is working again

3.4.6 - 2021-11-04
------------------

[#46395] Fix missing route

3.4.5 - 2021-10-28
------------------

[#46561] Cache LoRa Connector to allow for proper DataLoader usage in lora.py
[#46561] Fix get_configured_organisation broken on cold cache

3.4.4 - 2021-10-26
------------------

[#46389] Fix bug in employee validation

3.4.3 - 2021-10-26
------------------

[#46522] Proper caching for LoRa DataLoader

3.4.2 - 2021-10-22
------------------

[#46504] Fix memory leak caused by `in_separate_thread` introduced in 718bfa5e.

3.4.1 - 2021-10-21
------------------

[#46389] Bugfix update logic when forcing a new parent on an org unit

3.4.0 - 2021-10-21
------------------

[#46067] Optimise fetching from LoRa using Strawberry DataLoader.
[#46024] Send parameters to lora through HTTP GET body as JSON.

3.3.0 - 2021-10-18
------------------

[#43749] Further work on GraphQL

3.2.0 - 2021-10-18
------------------

[#45841] Add legacy auth session support

3.1.0 - 2021-10-12
------------------

[#45717] V1 API moved behind feature flag pending removal

3.0.1 - 2021-10-12
------------------

[#44886] Fix missing '/indsigt' route in backend

3.0.0 - 2021-10-11
------------------

[#46240] Update LoRa to version 2.1.0. Most users will want to set LORA_AUTH=false in their environment.
[#46240] Update Keycloak Realm Builder to version 2.3.0.

2.7.0 - 2021-10-11
------------------

[#46170] Allow a limited termination period on org functions

2.6.0 - 2021-10-09
------------------

[#45051] Made DAR lookups async using os2mo-dar-client

2.5.0 - 2021-10-08
------------------

[#46142] Converted our AMQP Trigger to be async

2.4.4 - 2021-09-27
------------------

[#45211] Read OS2mo version and commit sha from build arg environment variables

2.4.3 - 2021-09-27
------------------

[#45924] Fix performance issues caused by introduction of httpx.

2.4.2 - 2021-09-24
------------------

[#45886] Add LoRa HTTPX client timeout configuration. Fixes a bug where requesting large OU trees would time out.

2.4.1 - 2021-09-24
------------------

[#44432] Fix race-condition in bulking cache.
[#45482] Fix bulking for OrgUnit and Facet.

2.4.0 - 2021-09-23
------------------

[#43749] Added GraphQL endpoint and single endpoint

2.3.0 - 2021-09-09
------------------

[#44120] Allow searching for engagement associations by org unit.

2.2.2 - 2021-09-07
------------------

[#43749] Add poetry to build project

2.2.1 - 2021-09-06
------------------

[#44806] Fix TestCafe no longer be reliant on an actual config database

2.2.0 - 2021-09-06
------------------

[#45028] Fix and extend support for historic values in v1 API by supporting new `?validity=<start>/<end>` syntax.

2.1.6 - 2021-09-03
------------------

[#41555] Second attempt on introducing salt-automation fluxcd automatic image updater for dev

2.1.5 - 2021-09-03
------------------

[#41555] Introduce salt-automation fluxcd automatic image updater for dev

2.1.4 - 2021-09-03
------------------

[#44747] Fold up v1 endpoints.

2.1.3 - 2021-09-02
------------------

[#45263] Only perform token UUID check when RBAC is enabled

2.1.2 - 2021-09-02
------------------

[#44918] Don't crash if asked to update a nonexistent LoRa object

2.1.1 - 2021-08-30
------------------

[#41555] Run tests in parallel.

2.1.0 - 2021-08-27
------------------

[#44747]: Added Pydantic models to v1 API endpoints.

2.0.1 - 2021-08-26
------------------

Optimized GitLab CI to only run the absolutely necessary tasks.

2.0.0 - 2021-08-26
------------------

New features
------------
* #45211: Added commit shas and tags to docker images.
* #44806: Role-bases access control (RBAC) for the employee part of the system. See notes about configuration in the documentation.
* #44082: Role-based access control (RBAC) for the organization part of the system. The feature is enabled via an ENV variable
* #43998: Rework docker-compose.yaml and made database-backing on confdb configurable.
* #44744: Cleaned up tags in the OpenAPI docs endpoint (/docs)
* #44744: Added keycloak support on the OpenAPI docs endpoint (/docs)
* #44717: Added confdb environment settings, adjusted confdb healthcheck, disabled set configuration endpoints
* #44746: Expanded AMQP events with service-uuid, cleanup in trigger module
* #43364: Added sslmode to database connection options
* #44187: Add structured logs. Improvements to debugging/troubleshooting
* #42774: Add English translation. The user can now choose Danish or English screen texts by clicking the flags in the nav bar
* #42869: Added delta-api parameter "changed_since" to /api/v1/ endpoints
* #43544: Keycloak authentication. Keycloak container, DB and config added
* #41560: New org-funk: Owners
* #44181: Add Opentelemetry instrumentation
* #43364: Reimplement settings using Pydantic and environment variables
* #37599: Users can now terminate organisation unit registrations (as an alternative to terminating the entire organisation unit)
* #44188: Add local Grafana/OpenTelemetry development environment (:3000/explore)
* #44596: Implement Prometheus FastAPI instrumentor, new metrics endpoint with version and health checks
* #38239: Users can now search on more properties of employees and organisation units.
* #39858: Users can now see additional properties of employees and organisation units in the search results, if configured.
* #44530: Speed up the search for matching organisation units from the "org unit picker", if configured.

Bug fixes
---------

* #44674: Editing an organisation unit's start date caused the wrong start date to be used

OLD CHANGELOG BELOW
===================

Version 1.18.1, 2021-07-07
==========================

Bug fixes
---------

* #44470: Fix request flags bleeding through to other requests

Bug fixes
---------

* #44470: Fix request flags bleeding through to other requests

Version 1.18.0, 2021-07-01
==========================

New features
------------
* #40933: "Create employee" dialog now allows creating an employee without any engagements

Bug fixes
---------
* #42821: The search input field sometimes "swallowed" the first few characters typed. Fixed.

Version 1.17.2, 2021-07-01
==========================

Bug fixes
---------

* #44281: Fix LoRa HTTP connector

Version 1.17.1, 2021-06-18
==========================

Bug fixes
---------

* #44071: Fix HTTP trigger integration

Version 1.17.0, 2021-05-12
==========================

New features
------------
* #42778: Make CPR optional
* #42073: New /api/v1/ endpoints introduced, API currently still unstable
* #42779: Added new address scope: Multifield Text (2-fields)
* #41914: Replaced Flask with FastAPI
* #42780: Added seniority field (and conf_db setting to hide it)
* #42034: Added entities as proper frontend entity (behind configuration)
* #42864: Added new org_func: engagement_association, linking engagements to org_units
* #42033: Improved on the UI-aspects of extension_X fields
* #42920: Added create and update facet class endpoint
* #43300: Implement auth for FastAPI

Version 1.16.1, 2021-04-20
==========================

Bug fixes
---------
* #43091: Fix DAR health endpoint timeout issue

Version 1.16.0, 2021-04-06
==========================

New features
------------
* #41387: Allowed frontend to create and edit (but not move) root units
* #38904: Deprecated read-only
* #39857: When selecting an organisation unit from a tree dropdown, you can now type to search by name
* #40863: MO backend can now expose the number of associations and engagements in each organisation unit
* #41658: Run Vue unittests in Gitlab CI. This adds a new 'Build frontend' step to our 'build' stage, as well as a new 'Vue-unit-tests' stage to our 'test' stage
* #39853: Users can now specify a date when searching. This allows finding inactive organisation units, etc.
* #41915: Prepare MO to utilize FastAPI LoRa.
* #42112: Allow UI to set and change engagement ID (bvn)
* #42033: Made extension_X fields on engagements UI-wise configurable in conf_db
* #41973: Allowed addresses pointing to engagements
* #41894: Added refresh trigger event
* #40932: Users can now filter the displayed organisation unit tree if the new facet 'org_unit_hierarchy' is set up.

Version 1.15.0, 2021-03-08
==========================

New features
------------

* #40700: Added HTTP(s) Trigger system

Bug fixes
---------

# 41952: Bugfix: facet children not properly ported to async

Version 1.14.1, 2021-03-04
==========================

Bug fixes
---------

* #40621: Allow vacant associations, creatable from organisation unit
* #40719: Simplify validations for edits involving org units

Version 1.14.0, 2021-02-11
==========================

New features
------------

* #40303: Add "Links" dropdown to top navigation, displaying custom links for an organisation
* #40960: Performance improvement: Bulk calls to lora (with request-wide cache , but  without automation-magic)

Version 1.13.0, 2021-01-22
==========================

New features
------------
* #40619: Added substitute to associations tab under organisations
* #40828: Remove `default_page_size` parameter, making paged endpoints return the full sized result per default
* #40828: Remove `tree_search_limit` parameter
* #39316: Addresses using TEXT scope are now displayed and edited as multiline text
* #39859: The "Organisation" page layout (split) can be controlled by the user
* #40177: Edit nickname as two separate fields (given name and surname)
* #39841: Fix time machine date picker
* #40620: Improved association presentation and extended the editing capabilities in the UI

Bug fixes
---------
* #39855: When editing employees, sometimes misleading error messages were displayed

Version 1.12.0, 2021-01-08
==========================

New features
------------

* #39858: Added field in ConfDB to optionally show user_key to searches
* #39856: Changed log messages from uuid to human readable, no functionality changed
* #40170: Fix bug in frontend, allowing better performance when moving organisations
* #40169: Ported lora connection to async, thereby achieving better performance
* #40678: Changed filtering process, thereby achieving better performance
* #40695: Fix bug in facet children endpoint, bug introduced at async port

Version 1.11.0, 2020-12-14
==========================

New features
------------

* #39323: Remove request size limit for uuid lookup against LoRa,
          MOX should now be started with `--limit-request-line 0`
* #38650: Config value migrated from VARCHAR to TEXT
* #38650: Alembic introduced for ConfDB migration
* #40028: Remove history icon from GUI
* #39418: Disable typing in tree-picker GUI elements
* #39370: Reordered organization (facet) and substitute fields, no functionality changed
* #39375: Added configuration option for hiding cpr_no from UI
* #39367: Fix backend issue when editing associations

Version 1.10.2, 2020-11-13
==========================

New features
------------

* #39244: Added root filter to orgunit search
* #39244: Unified the paged_filtered_get and paged_get methods, thus changing
  the order of paged lists throughout MO. The order is now by UUID instead of
  by user_key / bvn.
* #39468: Fix bug where UI query page didn't work with Excel files


Version 1.10.1, 2020-10-26
==========================

New features
------------

* #38941: Fix bug where it was possible to create KLE objects without 'aspect'
* #38788: Implement uuid search filters


Version 1.10.0, 2020-10-23
==========================

New features
------------

* #35785: Fix bug where Flask would lock the database during requests with
  auth, preventing other concurrent requests
* #39199: Fix bug where UI facet pickers would not use existing values when editing

Version 1.9.2, 2020-10-19
=========================

New features
------------

* #38909: Added Configurable CORS.
* #38973: Update class/facet service endpoints to only return minimal set of data,
  with options to return individual additional attributes.
* #38973: Add internal speedups for bulk get requests towards LoRa
* #38041: Enables filtering facet classes based upon the selected org-unit.
          This applies only to creating new org-units.

Version 1.9.1, 2020-10-06
=========================

Bug fixes
---------

* #38803: Handle employees not having a user_key


Version 1.9.0, 2020-09-18
=========================

New features
------------

* #38237: Removed an expensive superfluous search filter from employee search.
* #38398: The create dialog for the various relations now allow the user to
          create multiple objects at once.

Bug fixes
------------
* #35937: Fix an issue regarding binding dynamic classes to associations during
          association creation. Previously the binding was only created during
          edits.

Version 1.8.1, 2020-09-14
=========================

New features
------------

* #38371: Enabled configuration setting to toggle whether a
          manager should be inherited in the UI for a given org unit.

Version 1.8.0, 2020-09-11
=========================

New features
------------

* #35937: Removed a duplicate entry from backend/mora/mapping.py
* #35937: Parameterized ancestor tree helper function.
* #35937: Parameterized Tree Picker / Viewer
* #35937: Dynamic recursive facet / class picker on Association View.
          Which dynamic facets to show can be picked using the
          :code:`association_dynamic_facets` configuration variable in conf_db.
* #38241: Fixed bug in org unit validation preventing users from moving
  and terminating certain org units

Version 1.7.1, 2020-08-12
=========================

New features
------------

* #30083: Upgraded to Python 3.8.5


Version 1.7.0, 2020-08-11
=========================

New features
------------

* #30083: Upgraded to PostgreSQL 11 and Python 3.8.
* #36672: Add 'kaldenavn' to employees, with a separate UI tab for tracking
  changes.

Version 1.6.4, 2020-08-10
=========================

Bug fixes
------------

* #37553: Fix bug when trying to create leave without engagements

Version 1.6.3, 2020-07-10
=========================

New features
------------

* #37231: Remove the organisation page overview

Version 1.6.2, 2020-06-22
=========================

New features
------------

* #34943: Add support for specifying SP domain for SAML auth

Bug fixes
---------

* #34847: Update documentation for SAML auth
* #34849: Add more robust handling of deprecated settings
* #36952: Fix org unit end date picker being locked when editing
* #36953: Fix dates being off by one when reading from API


Version 1.6.1, 2020-04-03
=========================

New features
------------

* #35673: Add 'engagement' field to leave objects

Bug fixes
---------

* #35531: Fix org unit rename dialog error handling
* #35897: Fix conf_db health endpoint not catching certain errors
* #35992: Fix sticky backend errors in UI modals


Version 1.6.0, 2020-03-24
=========================

New features
------------
* #27622: Enable use of serviceplatformen/cpr exttest
* #28808: UI now shows the versions of OS2mo and LoRa, with links to
  release notes.
* #33525: Implement support for KLE annotations in OS2mo
* #33262: Employee list output now includes CPR numbers
* #34448: Implement read-only mode for OS2mo UI, toggled through an API.


Version 1.5.0, 2020-02-27
=========================

New features
------------

* #33975: Set today's date as default for datepicker.
* #32045: Fixed employee search for the first key press.
* #34444: Add tab routing for employee and organization.
* #31732: Adjust table columns.
* #34157: Add 10 generic extension fields to engagement objects

Internal changes
----------------

* #34430: Update LoRa dependency to 1.6.1
* #27622: Update service_person_stamdata_udvidet dependency to 0.2.0
* #34481: Add new defaults to config database


Version 1.4.0, 2020-01-22
=========================

New features
------------

* #32759: Add support for displaying a button on org units for triggering
  external integrations.
* #33761: Add org unit as auto default for select unit input field in
  OrganisationUnitMove.
* #33450: Add support for new data consolidation features in LoRa

Bug fixes
---------

* #34006: Inherited managers are now properly calculated when an existing
  manager is terminated
* #29417: It is no longer possible to delete an inherited manager

Internal changes
----------------

* #32417: Missing defaults for configuration database are now inserted
  individually during init_db
* #34178: Add support for specifying Flask `SERVER_NAME` for when the
  application is deployed behind a proxy


Version 1.3.0, 2019-12-11
=========================

New features
------------

* #32964: Added support for new primary and org unit level fields

Bug fixes
---------

* #33569: Changes in the past are now properly reimplemented for terminations,
  renames and moves.
* #33456: Configuration database initialization now only inserts default
  values if they are not present

Internal changes
----------------

* #32964: Refactored reading code


Version 1.2.0, 2019-12-04
=========================

New features
------------

* #29760: Best practises updated concerning OS2Sync integration
* #32467: We now once again allow performing edits in the past
* #31978: Better logs.
* #32838: Health endpoints have been implemented to show the status of OS2mo
  and the various systems on which it depends.

Bug fixes
---------

* #28830: Small update of configuration documentation
* #30983: Fixed editing org units not taking time planning user settings into
  account
* #31851: Date pickers are now properly locked to the validities of the
  associated org units

Internal changes
----------------

* #32713: Use Gitlab CI instead of Jenkins.
* Changed the way test are run:

  * #31797: Letting OS2mo use the LoRa defined in settings insead of creating
    one internally
  * #31758: Constructed a new small test dataset in JSON instead of the
    generated one in SQL for integration test. Update facets in test to reflect
    reality.
  * #31912: Use the new JSON test dataset for end-to-end tests and expand it
    greatly.
  * #31799: Seperate linting from unit and integration tests.
  * #31798: Seperate end-to-end test from unit and integration tests.

* Remove copy services by:

  * #32687: Copy :file:`db_extensions.json` to LoRa.
  * #32677: Move database setup to a new `postgres-os2mo
    <https://git.magenta.dk/rammearkitektur/postgres-os2mo>`__ image.


Version 1.1.0, 2019-10-09
=========================

New features
------------

* #32200: Implement configuration option to hide CPR numbers, so CPR values
  aren't returned from backend, and cannot be searched for.
* #32174: Update documentation for authentication and authorization
* #33033: Best practises expanded to cover payroll systems integration
* #29760: Best practises updated concerning OS2Sync integration


Version 1.0.0, 2019-10-04
=========================

New features
------------

* #29741: AMQP messages moved to new Trigger module (on-after)
* #30983: Make time planning field on org units hidden based on configuration
* #29129: Org unit location delimiter is now backslash
* #29417: Prevent users from editing inherited managers
* #32048: Prevent users from editing org unit user keys
* #32059: Visibility is now enabled for all address types

Bug fixes
---------

* #22316: Ensure update payloads sent to LoRa satisfy validation
  requirements
* #31661: ``org`` is now correctly an optional (deprecated) parameter on
  creation of various objects
* #29129: Fix org unit details modal not reacting to errors from backend when
  creating new objects
* #31851: Creating relations for org units now correctly takes the org unit
  validity into account when limiting the date pickers.
* #29604: Redirect to the page of a newly created org unit
* #29548: We now prevent the user from terminating managers (and other
  relations), before they are active.
* #32053: Return all klasser belonging to a facet, regardless of the page limit
  set in configuration

Internal changes
----------------

* #29626: DAR address objects can now be inserted regardless of whether DAR is
  up, using ``force``. DAR address objects in LoRa no longer include the
  'pretty' address, to simplify saving the object.
* #31732: Adjusted table and removed org_unit and engagement-ID from engagement
  and associatied tabs for organisation.


Version 0.21.0, 2019-09-04
==========================

API changes
-----------

``/service/e/create``:

Our validation now prevents creating an employee without a CPR number.
To bypass this check, specify ``force=1``.

New features
------------

* #29738: user_key can be entered in UI for organisational units. if none
  is entered, the uuid of the organisational unit is used like before
* #31024: Organisation drop down removed. Organisation has been moved
  into configuration values. Strictly enforced in 'production', less
  so in development / testing
* #27213: AMQP messages are sent whenever an object is created, edited or
  deleted which allows anyone to build custom & powerful integrations.
* #30094: Allow organisational units to have no addresses, rather than
  forcing them to have a phone and physical location.

Bug fixes
---------
* #29761: Date pickers moved to the top of the various forms
* #30093: The shown units in the organisation unit pickers now reflect
  the dates selected in the date pickers
* #29669: Fix terminating units past any date they've been changed in
  the future.
* #29700: Ensure that date dropdowns always focus a selectable date,
  rather than e.g. the creation date of an old unit.
* #29245: EAN and P-number validation now behave as expected
* #29244: We no longer automatically add +45 to phone numbers
* #29563: Fix renaming or moving units that have a termination date.
* #30095: Address missing error in CPR search by automatically
  performing said search. And filter out any dashes while at it.
* #29569: Validate addresses related to their unit and employee when
  editing rather than merely at creation.
* #29570: Ensure the error messages when validating a unit move are correct
  and in the correct locations.
* #31425: Better handling of addresses with empty 'brugervendtnoegle'
* #31029: We should no longer crash when reading orgfunk effects with more
  than one attribute


Version 0.20.1, 2019-07-15
==========================

This release only contains documentation fixes

Version 0.20.0, 2019-07-10
==========================

Internal changes
----------------

* #24130: The configuration module now has a public api, allowing for dynamic
  changes of the configuration options.
* #30233: Conf module and sessions module have been dockerized


Version 0.19.0, 2019-06-27
==========================

Internal changes
----------------

* #28686, #28687: Add Dockerfile for both production and development.
* #28804 MO now distinguishes between given name and surname.


Version 0.18.0, 2019-05-22
==========================

New features
------------

* #29234: AD integration cookbook added to documentation
* #26857: Removed manager address for create employee and employee and organisation tabs.

Bug fixes
---------

* #29019: Never ending loop in manager inheritance
* #28017: Changed style for user settings - location and user key.
* #29200: We now properly clear the store when switching org units/employees
  to prevent 'old data' from showing.
* #29200: Fixed spinners when loading table data.
* #29603: Spinner is now shown when tree view is loading

Internal changes
----------------

* #26407: Allow selecting optional components per deployment.

Version 0.17.0, 2019-04-30
==========================

New features
------------

* #25411: organisation units can show managers by inheritance from parent
* #28323: Added 'fraction' field to engagements
* #28563: Added feature for generating 'thin' responses when reading details,
  where only the UUIDs of relations are returned as opposed to deep lookups
  being performed.

Bug fixes
---------

* #28563: Fixed bug where attribute extensions were not used for chunking on
  reads

Version 0.16.0, 2019-03-22
==========================

New features
------------

* #27687, #27777: The various ``organisationfunktion`` relations now support both
  ``user_key`` and ``integration_data``.
* #25396: Implemented validation of individual fields in frontend using
  backend validation API.
* #25416: Added engagement ID to column engagement for employee and organisation.
* #26961: Add support for marking associations as “primary”.

Bug fixes
---------

* #27228: Clicking the “Save” button in the organisation mapper now
  shows a confirmation that the operation succeeded.
* #26402: The “Save” button on the organisation mapper now correctly
  deactivates when successfully saving changes.

Internal changes
----------------

* #27526: TestCafe test for employee association tab for create, edit and terminate popups.
* #27527: TestCafe test for organisation manager tab for create, edit and terminate popups.
* #27959: Documentation added on how to set up a SAML SSO instance for
  testing and development.


Version 0.15.1, 2019-03-19
==========================

* This release merely contains minor tweaks to the documentation.


Version 0.15.0, 2019-03-11
==========================

API changes
-----------

``/service/e/(uuid:employee_uuid)/terminate``:

The defaults for employee termination changed, and now affect managers
similarly to any other functions. To achieve the previous behaviour of
merely marking manager functions as *vacant*, set ``"vacant": true``
in the JSON request. Please note that this is the inverse of the
previous ``terminate_all`` parameter, which no longer has any affect.

Internal changes
----------------

* #27431: The ``address_property`` facet is now named ``visibility``.

New features
------------

* #27299: Config check on startup, DUMMY_MODE instead of PROD_MODE,
* #26459: Add support for terminating relations, such as associations,
  addresses, etc., using a separate dialog.
* #25575: Added visibility for addresses with a phone number and exposed them in columns -
  address, association and manager for employee and organisation.
* #25407: Added checkbox message alert validation for workflow employee terminate.
* #27336: Remove association addresses.
* #25174: Add support for marking engagements as “primary”.
* #27261: We can now read the username from the SAML session NameID
* #27290: Add support for assigning time planning to organisational units.

Bug fixes
---------

* #25671: Organisation is now properly set when creating new employee.
* #25694: Changed table columns layout to align between table future, present and past.
* #26886: Fixed duplicate for addresses in create organisation unit and
  employee move many workflow now works again.
* #27149: Dont show terminate button for employee detail tabs for workflows - employeeTerminate and
  employeeMoveMany.
* #27218: Fixed exception being thrown when creating new DAR addreses, where the address lookup fails.
* #27155: Ensure that we show all unit roots when reloading a unit page.
* #27153: Fixed the error and success messages for organisation and employee.
* #27488: Fixed 401 not redirecting to login

Version 0.14.1, 2019-02-22
==========================

New features
------------

* #27244: Associations no longer have job functions. 'Tilknytningstype' renamed to 'Tilknytningsrolle'.

Version 0.14.0, 2019-01-30
==========================

New features
------------

* #25405: Submit button for create new and edit modals for organisation
  units and employees is no longer disabled if the form is invalid
* #25394: It is now no longer possible to perform edits taking effect before
  the current date.
* #25100: It is now possible to optionally also terminate associated manager
  roles when terminating an employee.
* #24702: Allow marking organisational units as related to each other.
* #26368: Add support for using ``?validate=0`` as a query parameter
  for disabling certain validations.
* #25409: Added backend support for specifying visibility for phone number
  address objects.
* #25706: Added more meaningful error message when editing addresses.
* #25406: All text has been moved into a translation file
* #25404: A validation ensures that a person (cpr) cannot be created twice in the database

Internal changes
----------------

* #25577: Implemented more facets for address types and job functions.
  Updated handling of facets throughout.
* #26070: Input fields now inherit from a common base.
* #26531: Employee workflow stores are now only loaded when they are needed.
* #26551: Restructured how frontend files are organised.
* #26600: Some styling issues.
* #26604: Menu items and shortcuts can now be added via an internal API.
* #26675: Moved i18n and validation import into seperate files.
* #26658: Added constant names to global store.
* #25053: Addresses are now modeled using ``organisationfunktion``, in order
  to further streamline and unify the modeling of relations.
* #26686: Added documentation to frontend.

Bug fixes
---------
* #25405: Submit button for create new and edit modals for organisation
  units and employees is no longer disabled if the form is invalid
* #25028: Time machine is working again.
* #25579: Address race condition when quickly switching between units
  in the tree view at the left.
* #25186: Hidden person input for create employee manager.
* #25690: Ignore spacing in address type input field.
* #26368: Validation no longer prevents adding an association if it
  duplicates another *inactive* association.
* #25704: Set ``max-width`` on the detail view table columns to ensure consistent alignment.
* #25696: Added remove button for dates.
* #26890: Fixed regression that broke viewing the details of a unit in
  the termination dialog.
* #26898: Ensure that detail view for organisation mapper shows all
  related units.
* #26788: Fixed the manager edit popup to submit with a blank employee picker field.
* #26801: Adjust styling of missing address note for associations such
  that it no longer appears as an error.
* #26787: Added check for org unit valid dates in the datepicker.
* #26874: Added scrollbar overflow-x for table.
* #25697: Added scrollbars to the dropdown menu when choosing Unit in Create Employee
* #24493: Added indication of where a value is missing in Create Unit
* #24492: Name change was not reflected before the page was updated manually
* #24933: Internet Explorer stopped validating input fields. Works again now.

Version 0.13.0, 2018-11-30
==========================

New features
------------

* #24880: Switch to a new implementation of the tree view which allows
  rendering the tree view properly on load, keeps the selection
  updated when changing units, and eventually enables rendering
  filtered trees for to make searching easier.
* #24880: Implement LiquorTree in order to underpin the ability to
  map between Organizational units

Internal changes
----------------
* #21966 Implemented use of vuex for employee workflows.

* #23779: Added custom UUID url converter, stringifying UUID parameters in
  order to standardise our use of UUIDs internally.
* #24797: Integration data added to employee and organisational unit.
* #25136: Refactored front end code.
* #24700: Backend ready for the Phonebook

Known bugs
----------

* #25579: Quickly switching between org units in the tree causes a race condition.
* #25671: Newly created employees can not be found using the search function.

Version 0.12.0, 2018-11-16
==========================

New features
------------

* #23928: We now use our `Flask SAML SSO
  <https://github.com/magenta-aps/flask_saml_sso/>`_ module for
  authentication.
  Session is now shared between OS2MO and LoRa.
* #22382: Manager hierarchy - the service returns all managers in a
  hierarchical order
* #24077: We now support access addresses in addition to regular
  addresses from Dansk Adresseregister, with combined autocompletion
  of the two.


Internal changes
----------------

* #25193: Improved handling of external configuration files for OS2MO.
  A warning is no longer triggered on unknown settings.
* #24545: OS2MO 2.0 as an OS2 Level 3 Product
* #24664: Meet the requirements of the standard or explain why you do not
  https://mora.readthedocs.io/en/master/README.html?highlight=sag#lora-backend-model
* #24656: Documentation of the requirements for operating the solution
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24659: Only one version of the core code: https://github.com/OS2mo
* #24662: Best practice for implementing the solution in your organization
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24661: Presentation material
  https://www.magenta.dk/?service=rammearkitektur &
  https://os2.eu/projekt/os2mo
* #24663: Codestandards
  https://mora.readthedocs.io/en/master/README.html#kodestandarder
* #24665: Process plan for the implementation of the solution
  https://mora.readthedocs.io/en/master/cookbook.html#best-practices-for-implementering
* #24655: Open Source license criteria are met
  https://mora.readthedocs.io/en/master/README.html#licens-og-copyright


Bug fixes
---------
* #24738: Removed sorting and icons for some columns.

Known bugs
----------
* #25405: Validation errors when creating org unit relations outside of the
  parent org unit range are not properly shown in UI


Version 0.11.1 2018-11-02
==========================

Bug fixes
---------

* #25028: Timemachine now shows and updates the organisation unit
  view when changing organisation unit


Version 0.11.0, 2018-10-30
==========================

New features
------------
* #24547: Backend support for modifying the name and CPR number of employees.
* #24400: Better documentation of command line interface.
* #24750: Added functionality for listing and retrieving generated
  export files from external directory.
* #24092: Added functionality for creating managers through the
  organisation interface in UI, including vacant managers.
* #24131: Added a simple configuration module that makes it possible
  to hide remove fields and tabs in the UI.
* #23960: A new page in the UI, ``/forespoergsler``, offers CSV
  exports of certain specific queries.
* #23276: Support for synchronising user names and CPR numbers added
  to the agent for fetching personal data from *Serviceplatformen*.
* #24214: Added associations to employees in the MED-organisation in
  Ballerup Kommune.


Internal changes
----------------

* #21966: Implemented use of Vuex in frontend.
* #24654: Source code is relocated to the `OS2mo organisation
  <https://github.com/OS2mo>`_ on GitHub.
* #24658: Technical implementation available as a `sub-page on our
  ReadTheDocs site
  <https://mora.readthedocs.io/en/development/dev.html>`_.
* #24657: The solution is fully documented on `ReadTheDocs
  <https://mora.readthedocs.io/>`_.
* #24660: Communication documents for the business and strategic level
  created at:

  - `OS2mo’s næste sprint går i retning af OS2-produktet og udvikling
    af integrationer
    <https://os2.eu/blog/os2mos-naeste-sprint-gaar-i-retning-af-os2-produktet-og-udvikling-af-integrationer>`_
  - `Lokal rammearkitektur og IDM med OS2MO & OS2rollekatalog
    <https://os2.eu/blog/lokal-rammearkitektur-og-idm-med-os2mo-os2rollekatalog>`_.


Bug fixes
---------

* #24150:  When terminating an employee, mark any manager roles it
  possesses as vacant rather than terminating them.
* #24069: Handle DAR address errors gracefully, displaying the error
  message rather than suppressing all addresses.
* #24077: Allow entering DAR access addresses as well as regular
  adresses in all fields, and allow reading historical addresses.
* #24810: Support for Internet Explorer 11.
* #24570: Sorting now works after performing an update.


Known bugs
----------


Version 0.10.1-post1, 2018-10-12
================================

Bug fixes
---------

* A missing check for Node packages broke the `mox
  <http://github.com/magenta-aps/mox/>` test suite.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.


Version 0.10.1, 2018-10-08
==========================

New features
------------

* #22849: Updated SAML implementation, with support for signed requests,
  single sign-on and single logout.
* #22381: Replace 'Enhedsnummer' with a description of the location of the organisational unit.
* #23558: Added the possibility to create managers without employees through the ou endpoint, thus allowing for vacant manager positions.
* #24014: Since we now model IT systems using an
  ``organisationfunktion``, we can now represent the account name.
* #22849: Added handling for user permissions, giving a fitting error if a user attempts an action without the correct permissions.
* #23976: Employees with their associated relations can now be created with one API call. All requests are now validated before being submitted to LoRa, to prevent half-writes.
* #24134: Columns in the UI can now be sorted.
* #24135: Dropdowns are now alphabetically sorted.
* #24068: Clicking the OS2-icon in the top left corner now takes you to the landing page.
* #23793: Support has been added for P-nummer as address type.
* #23781: Managers now have a separate set of address types.

Internal changes
----------------

* #23559: REST API now uses and enforces ISO 8601 dates in all cases
  except history display. All ``from`` or ``to`` dates must either
  lack a timestamp or correspond to midnight, Central European time.
* #23559: The ``terminate`` endpoints for employees as well as units
  now read the date from the ``to`` field rather than ``from``.
* #24198: We now model IT systems using ``organisationfunktion``
  rather than a direct relation.
* #23558: The employee is now optional on managers.

API changes
-----------

* #24200: Move all writing and editing APIs from ``/service/ou`` and
  ``/service/e/`` to a shared endpoint ``/service/details``. This
  primarily means that writing operations no longer require knowledge of the
  user, allowing e.g. vacant managers.

Bug fixes
---------

* #24067: Fixed being able to edit root organisational units
* #23559: Display end dates *inclusively*, so that the year ends 31
  December rather than 1 January.

Known bugs
----------

* #24134: Sorting doesn't work after performing an update.

Version 0.9.0, 2018-09-07
=========================

New features
------------

* #23778: Support for IT-systems on units

Internal changes
----------------

* #23992: Updated API documentation and README
* #23993: Reorganisation of source code layout
* #23994: Refactoring of frontend code

Bug fixes
---------

* #24012: Fixed hotkey support
* #24013: Fixed rename unit dialog not being populated correctly

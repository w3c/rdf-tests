# SPARQL 1.2 Protocol Requirements — Additions over SPARQL 1.1

## Version 2026-05-15

This document captures the normative requirements that are **new in SPARQL
1.2 Protocol** relative to SPARQL 1.1 Protocol. The full set of requirements
that a conformant SPARQL 1.2 service must satisfy is the union of:

- the SPARQL 1.1 Protocol requirements, recorded in
  [`../../sparql11/protocol/requirements.md`](../../sparql11/protocol/requirements.md);
  and
- the SPARQL 1.2-specific additions below.

The source is the SPARQL 1.2 Protocol Working Draft
(`sparql12-protocol.html`, editors' draft of 14 August 2025). Requirement
identifiers (`REQ-S.M.N[a]`) and section references (`Rec §S.M.N`) point
into that recommendation.

Where an obligation level is inferred from non-emphasised text or from
constraints in the recommendation's summary tables (rather than an
explicit RFC 2119 keyword in prose), the requirement is marked with a
dagger (†).

## What's New in SPARQL 1.2 Protocol

Compared with SPARQL 1.1 Protocol, the 1.2 recommendation adds:

1. A **version announcement mechanism** (§2.1) — clients can declare the
   SPARQL version of a query or update via:
   - the syntactical `version` directive in the query/update string;
   - a `version` parameter on the request (query string or form-encoded
     body, depending on HTTP method); or
   - a `version` media-type parameter on the `application/sparql-query` /
     `application/sparql-update` Content-Type header.
2. The corresponding parameter slots on query and update requests
   (REQ-3.1.3 / REQ-4.1.3 and the cardinality-restricting REQ-3.1.3a /
   REQ-4.1.3a).
3. Extensions to the Content-Type requirements for direct POST that
   permit a `version` media-type parameter (annotations to REQ-3.4.3 /
   REQ-4.3.3 in the SPARQL 1.1 requirements doc).
4. Updated normative references — RFC 9110 (HTTP Semantics) replaces
   older HTTP specifications.

All other SPARQL 1.1 Protocol requirements are inherited unchanged.

## Functional Requirements (new in 1.2)

### 2. Version Announcement

#### 2.1 Request Version Announcement
- **REQ-2.1.1** [MAY] (Rec §2.1): The client may announce the version of a query or update operation by using the syntactical `version` directive in the query/update string.
- **REQ-2.1.2** [MAY] (Rec §2.1): The client may announce the version of a query or update operation by passing a `version` parameter (via query string or form-encoded body, depending on HTTP method).
- **REQ-2.1.3** [MAY] (Rec §2.2.3, §2.3.2): The client may announce the version of a query or update operation by including a `version` media-type parameter on the `application/sparql-query` or `application/sparql-update` content type.
- **REQ-2.1.4** [MUST]† (Rec §2.1): When the version is indicated both in syntax and as a parameter and the values differ, the service shall use the version from the parameter and may emit a warning about the mismatch.
  > **Note:** The recommendation uses plain text ("parsers use the version from the parameter and might emit a warning"), not an emphasized RFC 2119 keyword. The obligation level is inferred.

#### 2.2 Response Version Announcement
- **REQ-2.2.1** [MAY] (Rec §2.1): Responses to an operation may contain version announcements. The response version (SPARQL results version or RDF version) is not necessarily the same as the operation version specified in the request; it is dependent on the response format.

#### 2.3 Version Announcement Guidance
- **REQ-2.3.1** [SHOULD NOT]† (Rec §2.1): To retain compatibility with older parsers, queries that do not make use of SPARQL 1.2-specific functionality should not announce a version.
  > **Note:** The recommendation uses "discouraged" rather than the RFC 2119 keyword SHOULD NOT.

### 3. Query Operation — version parameter

These extend the 1.1 Query Operation requirements documented at
[`../../sparql11/protocol/requirements.md#3-query-operation`](../../sparql11/protocol/requirements.md).

- **REQ-3.1.3** [MAY] (Rec §2.2): Client requests for the query operation may include a version (parameter name: `version`).
- **REQ-3.1.3a** [MUST NOT]† (Rec §2.2, table): Client requests for the query operation shall not include more than one `version` parameter.
  > **Note:** Inferred from table constraint "version (0 or 1)" and the singular "a version" in the text. No explicit RFC 2119 MUST NOT in the recommendation.

### 4. Update Operation — version parameter

These extend the 1.1 Update Operation requirements documented at
[`../../sparql11/protocol/requirements.md#4-update-operation`](../../sparql11/protocol/requirements.md).

- **REQ-4.1.3** [MAY] (Rec §2.3): Client requests for the update operation may include a version (parameter name: `version`).
- **REQ-4.1.3a** [MUST NOT]† (Rec §2.3, table): Client requests for the update operation shall not include more than one `version` parameter.
  > **Note:** Inferred from table constraint "version (0 or 1)". No explicit RFC 2119 MUST NOT in the recommendation.

## Extensions to Inherited Requirements

The following SPARQL 1.1 requirements are extended (not replaced) in
SPARQL 1.2:

- **REQ-3.4.3** (Content-Type for direct POST queries) — the 1.2
  recommendation permits an optional `version` media-type parameter on
  `application/sparql-query`. The 1.1 form (`application/sparql-query`
  without parameter) remains valid. Test
  `query_post_direct_with_version_param` exercises the 1.2 form.
- **REQ-4.3.3** (Content-Type for direct POST updates) — the 1.2
  recommendation permits an optional `version` media-type parameter on
  `application/sparql-update`. Test
  `update_post_direct_with_version_param` exercises the 1.2 form.

The base requirements are recorded in
[`../../sparql11/protocol/requirements.md`](../../sparql11/protocol/requirements.md).
This document does not duplicate them.

## Test-to-Requirement Mapping

The manifest [`manifest.ttl`](manifest.ttl) in this directory contains
the six tests that exercise the 1.2-specific additions. Every test
carries two `rdfs:comment` annotations: one linking it to the
requirement(s) it tests, and one identifying the source section in the
recommendation.

| Test | Requirements | Recommendation §§ |
|------|--------------|-------------------|
| `query_get_with_version` | REQ-2.1.2, REQ-3.1.3 | §2.1, §2.2 |
| `query_post_direct_with_version_param` | REQ-2.1.3, REQ-3.4.3* | §2.1, §2.2.3 |
| `bad_query_multiple_versions` | REQ-3.1.3a | §2.2 |
| `update_post_form_with_version` | REQ-2.1.2, REQ-4.1.3 | §2.1, §2.3 |
| `update_post_direct_with_version_param` | REQ-2.1.3, REQ-4.3.3* | §2.1, §2.3.2 |
| `bad_update_multiple_versions` | REQ-4.1.3a | §2.3 |

*Asterisked requirements (REQ-3.4.3, REQ-4.3.3) are defined in the
SPARQL 1.1 requirements document; this manifest exercises the 1.2
extension (the `version` media-type parameter).

### Requirement-to-Test Inverse Mapping

| Requirement | Tests |
|-------------|-------|
| REQ-2.1.1 | *(syntactical directive — exercised at the language level; no dedicated protocol test)* |
| REQ-2.1.2 | `query_get_with_version`, `update_post_form_with_version` |
| REQ-2.1.3 | `query_post_direct_with_version_param`, `update_post_direct_with_version_param` |
| REQ-2.1.4 | *(syntax/parameter mismatch handling — server policy, no dedicated test)* |
| REQ-2.2.1 | *(response version annotation — depends on response format, no dedicated test)* |
| REQ-2.3.1 | *(client guidance, not a server requirement)* |
| REQ-3.1.3 | `query_get_with_version` |
| REQ-3.1.3a | `bad_query_multiple_versions` |
| REQ-4.1.3 | `update_post_form_with_version` |
| REQ-4.1.3a | `bad_update_multiple_versions` |

## Requirements Without Dedicated Tests

| Requirement | Level | Rationale |
|-------------|-------|-----------|
| REQ-2.1.1 | MAY | The syntactical `version` directive is a feature of the SPARQL Query/Update language, not of the protocol. It is covered by the SPARQL 1.2 Query and Update language test suites. |
| REQ-2.1.4 | MUST† | Requires the server to detect mismatch between the syntactical `version` and the parameter `version` and prefer the parameter. Possible in principle but requires injecting a syntactically-versioned query whose syntactical version differs from the parameter; the obligation is also weak (inferred from non-emphasised "might emit a warning") so a conformance test is not warranted. |
| REQ-2.2.1 | MAY | Response version announcement is delegated to the response serialisation format (SPARQL Results JSON/XML, RDF). The presence of a version in the response is not a protocol-level decision and is not tested at the protocol level. |
| REQ-2.3.1 | SHOULD NOT† | A guidance directive to clients (do not announce a version unless using 1.2 features). Not a server obligation; no service-side conformance criterion. |

## Cross-References

- **Recommendation**: `sparql12-protocol.html` (W3C Working Draft, 14 August 2025).
- **Inherited 1.1 requirements**:
  [`../../sparql11/protocol/requirements.md`](../../sparql11/protocol/requirements.md).
- **Inherited 1.1 manifest**:
  [`../../sparql11/protocol/manifest.ttl`](../../sparql11/protocol/manifest.ttl).
- **This manifest**: [`manifest.ttl`](manifest.ttl).
- **Project summary**: [`../../protocol-tests.md`](../../protocol-tests.md).

## Normative References

The SPARQL 1.2 Protocol normatively references the same specifications
as SPARQL 1.1 Protocol, with the following changes:

- **RFC 9110**: HTTP Semantics — replaces older HTTP specifications
  used by SPARQL 1.1 Protocol.
- **SPARQL12-QUERY**, **SPARQL12-UPDATE**, **SPARQL12-GRAPH-STORE-PROTOCOL**,
  **SPARQL12-RESULTS-XML**, **SPARQL12-RESULTS-JSON**,
  **SPARQL12-RESULTS-CSV-TSV** — replace the corresponding 1.1
  specifications.
- **RDF12-CONCEPTS**, **RDF12-TURTLE**, **RDF12-XML** — replace the
  corresponding RDF 1.1 specifications.

See the 1.1 requirements document for the full list of inherited
references.

## Analysis Notes

### A.1 Why this document is separate from the 1.1 requirements

The recommendation `sparql12-protocol.html` consolidates all 1.2 Protocol
requirements (inherited and new) in a single document. For test-suite
maintenance, however, it is convenient to:

- record the 1.1 base in the sparql11 directory, where the 1.1 manifest
  already lives; and
- record only the 1.2 additions here, alongside the manifest containing
  the 1.2-specific tests.

This split mirrors the inheritance model of the protocol itself: a
conformant 1.2 service is a conformant 1.1 service plus the 1.2
extensions.

### A.2 Cardinality requirements (REQ-3.1.3a, REQ-4.1.3a)

REQ-3.1.3a and REQ-4.1.3a are inferred from the "version (0 or 1)"
entries in the parameter tables of Rec §2.2 and §2.3. The recommendation
prose does not contain an explicit RFC 2119 MUST NOT for the multiple-
version case, but the table constraint together with the singular
phrasing "a version" makes the interpretation clear. The corresponding
tests (`bad_query_multiple_versions` / `bad_update_multiple_versions`)
verify that a service rejects requests with two `version=` values.

### A.3 Status of REQ-3.4.3 / REQ-4.3.3

These remain in the 1.1 requirements document because their core
content — that the Content-Type of a direct POST body must be
`application/sparql-query` or `application/sparql-update` — is
unchanged. The 1.2 recommendation extends them with an optional
`version` media-type parameter (e.g.
`application/sparql-query; version=1.2`). The 1.2 manifest's
`query_post_direct_with_version_param` and
`update_post_direct_with_version_param` tests exercise the extension;
the cross-reference to REQ-3.4.3 / REQ-4.3.3 in the inherited document
is intentional.

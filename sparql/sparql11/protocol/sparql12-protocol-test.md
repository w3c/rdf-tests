# SPARQL 1.2 Protocol Test Suite

This is a conformance test suite for the SPARQL 1.2 Protocol recommendation,
comprising a machine-readable requirements document, a test manifest in
Turtle, a set of RDF data files, and a Node.js test runner that executes
the tests against a SPARQL endpoint and produces an EARL report.

The project was developed in three stages:

1. **Requirements document** — extracted from the protocol recommendation.
2. **Manifest revisions** — upstream SPARQL 1.1 tests were merged with
   SPARQL 1.2-specific tests, corrected against the requirements, and
   annotated with dataset specifications.
3. **Test runner** — a Node.js implementation that reads the manifest,
   initialises the target repository via the Graph Store Protocol, issues
   the HTTP requests prescribed by each test, validates the responses, and
   records the outcomes.

Files produced by the project:

| File | Description |
|------|-------------|
| `sparql12-protocol-requirements-20260412.md` | Numbered requirements extracted from `sparql12-protocol.html` |
| `rdf-tests/manifest.ttl` | Turtle manifest of 48 protocol tests with requirement annotations |
| `rdf-tests/data1.nt`, `data2.nt`, `data3.nt` | RDF datasets referenced by `ut:graphData` |
| `sparql12-protocol-test.mjs` | Node.js test runner |
| `sparql12-protocol-earl.ttl` | EARL report output (written by the runner) |

---

## 1. Requirements Document

The source is the SPARQL 1.2 Protocol Working Draft
(`sparql12-protocol.html`, editors' draft of 14 August 2025). Each
normative statement that uses an RFC 2119 keyword (MUST, SHOULD, MAY,
MUST NOT, SHOULD NOT) was extracted and given an identifier of the form
`REQ-S.M.N[a]`, where `S.M.N` mirrors the recommendation's subsection
numbering.

The resulting requirements document,
`sparql12-protocol-requirements-20260412.md`, contains 89 numbered
requirements grouped into nine sections:

- **1. HTTP Foundation** — general HTTP conformance
- **2. Version Announcement** — the new SPARQL 1.2 `version` mechanism
- **3. Query Operation** — GET, URL-encoded POST, direct POST, dataset
  specification, content negotiation, success/failure responses
- **4. Update Operation** — URL-encoded POST, direct POST, dataset
  specification, success/failure responses
- **5. Base IRI Resolution** — service-defined BASE URI and the BASE
  keyword in queries
- **6. Response Formats** — serialisation requirements for each query
  form
- **7. Security and Policy** — denial-of-service protection, update
  security, IRI security
- **8. Conformance** — conformance criteria for protocol services
- **9. Internationalization** — charset requirements for SPARQL content
  types

Requirements whose obligation level is inferred from non-emphasised text
or from summary tables (rather than an explicit RFC 2119 keyword in
prose) are marked with a dagger (†) and called out in the Analysis
Notes. The document also tracks asymmetries between the recommendation's
treatment of queries and updates — for example, UTF-8 is explicitly
required only for `application/sparql-query`, not for
`application/sparql-update`, even though both content types carry SPARQL
text.

Appendix B of the document provides the test-to-requirement mapping:

- **B.1** — the corrected mapping from each test to the requirements it
  exercises, with the rationale for each correction.
- **B.2** — summary of the 27 incorrect requirement references found in
  the original manifest's `rdfs:comment` fields.
- **B.3** — the inverse mapping, from each requirement to the tests that
  reference it.
- **B.4** — requirements that have no dedicated test, with an explanation
  for each (usually because the requirement is implicitly exercised by
  other tests, or because its obligation level makes it untestable
  without server configuration).

---

## 2. Manifest Revisions

The upstream manifest (`rdf-tests/manifest.ttl`) originally contained
the 34 SPARQL 1.1 Protocol tests. The revisions:

### 2.1 Merged the 12 SPARQL 1.2-specific tests

These exercise the SPARQL 1.2 version mechanism, content negotiation,
and BASE IRI resolution:

- `query_get_with_version`, `query_post_direct_with_version_param`
- `update_post_form_with_version`, `update_post_direct_with_version_param`
- `bad_query_multiple_versions`, `bad_update_multiple_versions`
- `bad_query_get_with_body`
- `query_content_negotiation_xml`, `query_content_negotiation_json`
- `query_dataset_default_graph` (single-graph variant)
- `query_base_uri`, `update_base_uri`

### 2.2 Corrected requirement references

Every test has an `rdfs:comment "Tests REQ-…"` annotation pointing to the
requirements it validates. The original manifest's annotations used an
obsolete numbering scheme in which 27 of 45 test references were
incorrect — most notably a reference to the non-existent `REQ-3.2.6`.
Appendix B.1 of the requirements document records each correction with
its rationale.

### 2.3 Added recommendation-section annotations

Alongside the requirement annotation, each test now carries a second
annotation `rdfs:comment "Rec §…"` identifying the subsection of the
recommendation that defines the requirements being tested. For example:

    :query_get rdf:type mf:ProtocolTest ;
        rdfs:comment "Tests REQ-3.1.1, REQ-3.2.1" ;
        rdfs:comment "Rec §2.2, §2.2.1" ;
        ...

### 2.4 Reformulated the BASE IRI tests

The original `query_base_iri` and `update_base_uri` tests used `SELECT`
queries whose expected result was described in prose
(`mf:expectation "one result with ?o bound to an IRI that is _not_
<test>"`), which a test runner cannot programmatically verify.

The revised versions (now named `query_base_uri` and `update_base_uri`)
are ASK queries with machine-checkable boolean expectations:

- `update_base_uri` inserts a triple with the relative IRI `<test>` and
  then ASKs that the stored object is an IRI other than the unresolved
  `<test>` — proving that the service resolved the relative IRI against
  its base.
- `query_base_uri` inserts a triple via direct POST update (changed from
  URL-encoded POST), then uses `BASE <http://example.org/>` in an ASK
  query with relative IRIs, verifying that the client-supplied BASE
  resolves correctly.

### 2.5 Added additional tests

Three tests were added to cover requirements that had no dedicated test:

- **`bad_update_form_body_missing`** — URL-encoded update POST with the
  `update` parameter in the query string rather than the body. Tests
  REQ-4.2.2 (all parameters shall be in the body for URL-encoded POST).
- **`query_post_form_dataset`** — URL-encoded query POST where
  `default-graph-uri` is in the form body alongside `query`, rather than
  in the URL query string. Tests the Rec §2.2.2 idiom more faithfully
  than `query_post_form`.
- **`bad_multiple_queries_form`** — counterpart to `bad_multiple_queries`
  (which uses GET) that sends two `query=` parameters in a URL-encoded
  POST body.

### 2.6 Added dataset specifications

Every test now carries at least one `ut:graphData` property enumerating
the RDF file(s) to load into the repository before the test runs. The
upstream manifest specified graph data only for tests that query a
particular dataset; the revision adds a default
`ut:graphData [ ut:graph <data1.nt> ; rdfs:label "…/data1.rdf" ]` to
every other test so that endpoints have a known starting state. Three
data files (`data1.nt`, `data2.nt`, `data3.nt`) were created, each
containing a single `foaf:Document` typing triple.

References to the previously-used `data0.rdf` were replaced with
`data1.rdf`.

### Final manifest state

The revised manifest contains **48 tests** — the 34 upstream tests plus
the 12 SPARQL 1.2 tests plus two new tests — each annotated with
requirement identifiers, recommendation section references, and dataset
specifications.

---

## 3. Test Runner

`sparql12-protocol-test.mjs` is a Node.js ESM script that reads the
manifest, sets up each test's dataset, issues the HTTP requests
prescribed by the manifest, validates the responses against the
manifest's expectations, and produces an EARL report.

### 3.1 Dependencies

- Node.js 20 or later (native `fetch`, ESM)
- `n3` (Turtle parsing and in-memory RDF store)

Install with `npm install` in the project directory. The `package.json`
declares `"type": "module"` so that the `.mjs` file's `import`
statements resolve correctly.

### 3.2 Per-test execution flow

For each test in the manifest:

1. **Dataset setup** via the Graph Store Protocol. The runner iterates
   over the test's `ut:graphData` entries in document order:
   - The **first** entry is loaded with **PUT** to
     `<graph-store-url>?graph=<rdfs:label>`, which replaces the target
     graph's contents (clearing it before insertion).
   - **Subsequent** entries are loaded with **POST** to the same URL
     pattern for their respective graphs, appending data.
   - Files are read from the directory containing the manifest and
     submitted with `Content-Type: application/n-triples` and the bearer
     token.
2. **Test request(s)**. For multi-step tests (e.g. `update_base_uri`,
   which runs an update and then verifies it), the requests are issued
   in order. Each request:
   - Uses the HTTP method, path, body, and headers prescribed by the
     manifest.
   - When the manifest supplies no `ht:headers` and the body looks
     form-encoded, the runner adds
     `Content-Type: application/x-www-form-urlencoded` — but only when
     the test expects success (2XX/3XX); tests that expect only 4XX
     (the `bad_*_missing_*_type` tests) intentionally omit Content-Type.
   - Carries a `clientRequestId` URL parameter set to the test name, so
     that server access logs can be correlated with the manifest test
     that issued the request.
   - Always includes `Authorization: Bearer <token>`.
3. **Response validation**:
   - Status code matching against the expected pattern (`2XX`, `3XX`,
     `4XX`). When a test expects only 4XX and the client refuses to even
     send the request (e.g. Node's `fetch` rejecting a GET with body),
     the refusal counts as a pass because the request is itself
     invalid — which is exactly what the negative test asserts.
   - Response `Content-Type` checked against the manifest's
     `ht:headerElements` list when present.
   - Boolean body checked against the manifest's `cnt:chars true/false`
     or `mf:expectedBoolean` for ASK results, parsing SPARQL Results XML
     or JSON as appropriate.

Outcomes are recorded as `passed`, `failed`, or `cantTell` (used for
network errors on tests that do not expect 4XX, and for unparseable
responses).

### 3.3 EARL output

On completion the runner writes a Turtle EARL document:

- An `earl:Assertor` / `earl:Software` resource `<#tool>` describing
  the runner.
- An `earl:TestSubject` / `earl:Software` resource for the endpoint.
- One `earl:Assertion` per test, linking the assertor, subject, test
  IRI, execution mode (`earl:automatic`), and an `earl:TestResult` with
  the outcome, a human-readable `earl:info` detail, and a `dc:date`
  timestamp.

### 3.4 Invocation

```
node sparql12-protocol-test.mjs <endpoint-url> --token <token> [options]
```

Required arguments:

- `<endpoint-url>` — the SPARQL endpoint URL (HTTP/HTTPS). Example:
  `http://example.org/test/test/sparql`.
- `--token <token>` — bearer token added to every request's
  `Authorization` header. Required for private endpoints; required on
  the command line even if the endpoint is open, to make the test
  runner's authentication behaviour explicit.

Optional arguments:

- `--graph-store-url <url>` — Graph Store Protocol endpoint used for
  dataset setup. Default: derived from the endpoint URL by replacing
  the trailing `sparql` path segment with `service`. For example
  `http://host/test/test/sparql` is derived as
  `http://host/test/test/service`.
- `--tests <names>` or `-t <names>` — comma-separated list of test
  names or substrings. May be repeated. Only tests whose manifest
  identifier contains any of the supplied fragments are run. Default:
  all tests in the manifest.
- `--manifest <path>` — path to the Turtle manifest. Default:
  `./rdf-tests/manifest.ttl` relative to the runner's directory.
- `--earl-output <path>` — path for the generated EARL report. Default:
  `./sparql12-protocol-earl.ttl`.
- `--subject-name <name>` — human-readable name of the software under
  test, used as `doap:name` on the `earl:TestSubject`. Default: the
  endpoint URL's host.
- `--subject-uri <uri>` — URI identifying the software under test.
  Default: the endpoint URL itself.
- `-h`, `--help` — show usage and exit.

#### Examples

Run all tests against a local endpoint:

    node sparql12-protocol-test.mjs \
        http://localhost:3030/test/test/sparql \
        --token $TOKEN

Run only the query-direct-POST tests:

    node sparql12-protocol-test.mjs \
        http://localhost:3030/test/test/sparql \
        --token $TOKEN \
        -t query_post_direct

Run against an explicit graph-store URL and write the EARL report to a
specific path:

    node sparql12-protocol-test.mjs \
        https://example.org/api/sparql \
        --token $TOKEN \
        --graph-store-url https://example.org/api/data \
        --earl-output ./reports/example.ttl \
        --subject-name "Example SPARQL Service" \
        --subject-uri  https://example.org/api

### 3.5 Console output

The runner prints one line per test (`PASS`, `FAIL`, or `ERR`), a
summary of counts at the end, and the path to the EARL report. `FAIL`
and `ERR` lines are followed by an indented detail line containing the
reason (expected vs. actual status, unexpected Content-Type, boolean
mismatch, network error, or dataset-setup failure).

    SPARQL 1.2 Protocol Test Suite
    Endpoint:    http://localhost:3030/test/test/sparql
    Graph Store: http://localhost:3030/test/test/service
    Manifest:    …/rdf-tests/manifest.ttl (48 tests)
    ========================================================================
    PASS  bad_multiple_queries
    PASS  bad_multiple_queries_form
    FAIL  bad_query_get_with_body
          Request: Status: expected 4XX, got 200
    …
    ========================================================================
    Results: 42 passed, 5 failed, 1 errors (48 total)
    EARL report: …/sparql12-protocol-earl.ttl

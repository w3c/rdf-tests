# SPARQL 1.2 Protocol Requirements Document

## Version 2026-04-12

> **Revision note:** This revision corrects the test-to-requirement mapping in Appendix B, which was found to contain numerous errors in the 2026-04-11 version. The requirements themselves are unchanged; they have been verified against the recommendation (`sparql12-protocol.html`). The non-existent requirement "REQ-3.2.6" referenced in the manifest has been identified as an error — the correct requirement for UTF-8 encoding of direct POST queries is REQ-3.4.5 (or REQ-9.1.1).

This document captures the normative requirements defined by the SPARQL 1.2 Protocol specification (as provided in `sparql12-protocol.html`). Each requirement is derived from a MUST, SHOULD, or MAY constraint expressed in the specification (per RFC 2119) and is marked with its obligation level. Requirements are organized to support validation of conformant SPARQL Protocol services and clients.

Each requirement is annotated with its source subsection in the recommendation (e.g., "Rec §2.2.1"). Where an obligation level is inferred from non-emphasized text or table constraints rather than an explicit RFC 2119 keyword in the recommendation, this is marked with a dagger (†). See the [Analysis Notes](#analysis-notes) section for details.

## Protocol Overview

The SPARQL 1.2 Protocol defines an HTTP-based means of conveying SPARQL queries and updates from clients to SPARQL processing services and returning results. The protocol consists of two operations:

- **Query Operation**: For performing SPARQL Query Language queries (SELECT, ASK, CONSTRUCT, DESCRIBE).
- **Update Operation**: For performing SPARQL Update Language requests (INSERT, DELETE, LOAD, CLEAR, etc.).

The protocol is built on HTTP (RFC 9110) and is designed for compatibility with the SPARQL 1.2 Query Language and SPARQL 1.2 Update. A separate SPARQL 1.2 Graph Store Protocol covers RESTful management of named graphs.

## Terminology

The requirements below use the following terms as defined in the specification:

- **SPARQL Protocol client** (client): An HTTP client that sends HTTP requests for SPARQL Protocol operations.
- **SPARQL Protocol service** (service): An HTTP server that services HTTP requests and sends back HTTP responses for SPARQL Protocol operations.
- **SPARQL endpoint**: The URI at which a SPARQL Protocol service listens for requests.
- **SPARQL Protocol operation**: An HTTP request and response that conform to this protocol.
- **RDF Dataset**: A collection of a default graph and zero or more named graphs, as defined by the SPARQL 1.2 Query Language.

## Functional Requirements

### 1. HTTP Foundation

#### 1.1 HTTP Compliance
- **REQ-1.1.1** [MUST] (Rec §2): The service shall follow all HTTP requirements for requests and responses as defined in RFC 9110.
- **REQ-1.1.2** [MUST] (Rec §2.2.6, §2.3.4): The service shall use HTTP response status codes as defined in HTTP to indicate the success or failure of an operation.

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

### 3. Query Operation

#### 3.1 Query Operation General
- **REQ-3.1.1** [MUST] (Rec §2.2): The query operation shall be invoked with either the HTTP GET or HTTP POST method.
- **REQ-3.1.1a** [MUST] (Rec §2.2): The query request's parameters shall be sent according to one of the three defined options: query via GET (§2.2.1), query via POST with URL-encoded parameters (§2.2.2), or query via POST directly (§2.2.3).
- **REQ-3.1.2** [MUST] (Rec §2.2): Client requests for the query operation shall include exactly one SPARQL query string (parameter name: `query`).
- **REQ-3.1.3** [MAY] (Rec §2.2): Client requests for the query operation may include a version (parameter name: `version`).
- **REQ-3.1.3a** [MUST NOT]† (Rec §2.2, table): Client requests for the query operation shall not include more than one `version` parameter.
  > **Note:** Inferred from table constraint "version (0 or 1)" and the singular "a version" in the text. No explicit RFC 2119 MUST NOT in the recommendation.
- **REQ-3.1.4** [MAY] (Rec §2.2): Client requests for the query operation may include zero or more default graph URIs (parameter name: `default-graph-uri`).
- **REQ-3.1.5** [MAY] (Rec §2.2): Client requests for the query operation may include zero or more named graph URIs (parameter name: `named-graph-uri`).

#### 3.2 Query via GET
- **REQ-3.2.1** [MAY] (Rec §2.2.1): Protocol clients may send query requests via the HTTP GET method.
- **REQ-3.2.2** [MUST] (Rec §2.2.1): When using the GET method, clients shall URL percent-encode all parameters and include them as query parameter strings in the request URI (per RFC 3986).
- **REQ-3.2.3** [MUST] (Rec §2.2.1): HTTP query string parameters shall be separated with the ampersand (`&`) character.
- **REQ-3.2.4** [MAY] (Rec §2.2.1): Clients may include the query string parameters in any order.
- **REQ-3.2.5** [MUST NOT] (Rec §2.2.1): The HTTP request for query via GET shall not include a message body.

#### 3.3 Query via POST with URL-encoded Parameters
- **REQ-3.3.0** [SHOULD NOT]† (Rec §2.2, table): For query via URL-encoded POST, clients should not include SPARQL protocol parameters in the request URI query string; parameters should be conveyed in the form-encoded request body.
  > **Note:** Inferred from the table entry "None" for Query String Parameters in the URL-encoded POST row. No explicit RFC 2119 SHOULD NOT in the recommendation text.
- **REQ-3.3.1** [MAY] (Rec §2.2.2): Protocol clients may send query requests via the HTTP POST method by URL encoding the parameters.
- **REQ-3.3.2** [MUST] (Rec §2.2.2): When using this method, clients shall URL percent-encode all parameters and include them as parameters within the request body via the `application/x-www-form-urlencoded` media type.
- **REQ-3.3.3** [MUST] (Rec §2.2.2): Parameters shall be separated with the ampersand (`&`) character.
- **REQ-3.3.4** [MAY] (Rec §2.2.2): Clients may include the parameters in any order.
- **REQ-3.3.5** [MUST] (Rec §2.2.2): The content type header of the HTTP request shall be set to `application/x-www-form-urlencoded`.

#### 3.4 Query via POST Directly
- **REQ-3.4.1** [MAY] (Rec §2.2.3): Protocol clients may send query requests via the HTTP POST method by including the query directly and unencoded as the HTTP request message body.
- **REQ-3.4.2** [MUST] (Rec §2.2.3): When using this approach, clients shall include the SPARQL query string, unencoded, and nothing else as the message body of the request.
- **REQ-3.4.3** [MUST] (Rec §2.2.3): Clients shall set the content type header of the HTTP request to `application/sparql-query`, with an optional `version` media-type parameter.
- **REQ-3.4.4** [MAY] (Rec §2.2.3): Clients may include the optional `default-graph-uri` and `named-graph-uri` parameters as HTTP query string parameters in the request URI.
- **REQ-3.4.5** [MUST]† (Rec §2.2.3): UTF-8 is the only valid charset for the `application/sparql-query` content type.
  > **Note:** The recommendation states "Note that UTF-8 is the only valid charset here." The word "Note" and the absence of an emphasized RFC 2119 keyword make the formal obligation level ambiguous, though the normative intent is clear.

#### 3.5 Query RDF Dataset Specification
- **REQ-3.5.1** [MAY] (Rec §2.2.4): The RDF Dataset for a query may be specified via the `default-graph-uri` and `named-graph-uri` parameters in the SPARQL Protocol or in the SPARQL query string using the `FROM` and `FROM NAMED` keywords.
- **REQ-3.5.2** [MUST] (Rec §2.2.4): If different RDF Datasets are specified in both the protocol request and the SPARQL query string, then the service shall execute the query using the RDF Dataset given in the protocol request.
- **REQ-3.5.3** [MAY] (Rec §2.2.4): A service may reject a query with HTTP response code 400 if the service does not allow protocol clients to specify the RDF Dataset.
- **REQ-3.5.4** [MAY] (Rec §2.2.4): If an RDF Dataset is not specified in either the protocol request or the SPARQL query string, then implementations may execute the query against an implementation-defined default RDF dataset.

#### 3.6 Query Content Negotiation
- **REQ-3.6.1** [SHOULD] (Rec §2.2.5): Protocol clients should use HTTP content negotiation (RFC 9110) to request response formats that the client can consume.

#### 3.7 Query Success Responses
- **REQ-3.7.1** [SHOULD] (Rec §2.2.6): A protocol service should use a 2XX HTTP response code for a successful query.
- **REQ-3.7.2** [MAY] (Rec §2.2.6): A protocol service may choose instead to use a 3XX response code as per HTTP.
- **REQ-3.7.3** [MUST]† (Rec §2.2.6): The response body of a successful query operation with a 2XX response shall be either:
  - A SPARQL Results Document in XML, JSON, or CSV/TSV format (for SELECT and ASK query forms); or,
  - An RDF graph serialization (e.g., RDF/XML, Turtle, or equivalent) for DESCRIBE and CONSTRUCT query forms.
  > **Note:** The recommendation describes this definitionally ("The response body of a successful query operation with a 2XX response is either:...") without an emphasized RFC 2119 keyword. The normative force is implicit in the definitional structure.
- **REQ-3.7.4** [MUST]† (Rec §2.2.6): The content type of the response to a successful query operation shall be the media type defined for the format of the response body.
  > **Note:** The recommendation uses non-emphasized "must" — not formally RFC 2119 per the Document Conventions (§1.1).

#### 3.8 Query Failure Responses
- **REQ-3.8.1** [SHOULD]† (Rec §2.2.7): The service should return HTTP 400 if the SPARQL query supplied in the request is not a legal sequence of characters in the language defined by the SPARQL grammar.
  > **Note:** The recommendation lists this under "The HTTP response codes applicable to an unsuccessful query operation include:" without an emphasized RFC 2119 keyword. Obligation level is inferred.
- **REQ-3.8.2** [SHOULD]† (Rec §2.2.7): The service should return HTTP 500 if the service fails to execute the query. Services may also return a 500 response code if they refuse to execute a query.
  > **Note:** Same as REQ-3.8.1; no emphasized RFC 2119 keyword in the recommendation.
- **REQ-3.8.3** [MAY] (Rec §2.2.7): The response body of a failed query request is implementation defined. Implementations may use HTTP content negotiation to provide human-readable or machine-processable (or both) information about the failed query request.
- **REQ-3.8.4** [MAY] (Rec §2.2.7): A protocol service may use other 4XX or 5XX HTTP response codes for other failure conditions, as per HTTP.

### 4. Update Operation

#### 4.1 Update Operation General
- **REQ-4.1.1** [MUST] (Rec §2.3): The update operation shall be invoked using the HTTP POST method.
- **REQ-4.1.1a** [MUST] (Rec §2.3): The update request's parameters shall be sent according to one of the two defined options: update via POST with URL-encoded parameters (§2.3.1) or update via POST directly (§2.3.2).
- **REQ-4.1.2** [MUST] (Rec §2.3): Client requests for the update operation shall include exactly one SPARQL update request string (parameter name: `update`).
- **REQ-4.1.3** [MAY] (Rec §2.3): Client requests for the update operation may include a version (parameter name: `version`).
- **REQ-4.1.3a** [MUST NOT]† (Rec §2.3, table): Client requests for the update operation shall not include more than one `version` parameter.
  > **Note:** Inferred from table constraint "version (0 or 1)". No explicit RFC 2119 MUST NOT in the recommendation.
- **REQ-4.1.4** [MAY] (Rec §2.3): Client requests for the update operation may include zero or more default graph URIs (parameter name: `using-graph-uri`).
- **REQ-4.1.5** [MAY] (Rec §2.3): Client requests for the update operation may include zero or more named graph URIs (parameter name: `using-named-graph-uri`).

#### 4.2 Update via POST with URL-encoded Parameters
- **REQ-4.2.0** [SHOULD NOT]† (Rec §2.3, table): For update via URL-encoded POST, clients should not include SPARQL protocol parameters in the request URI query string; parameters should be conveyed in the form-encoded request body.
  > **Note:** Inferred from table entry "None" for Query String Parameters. No explicit RFC 2119 SHOULD NOT in the recommendation text.
- **REQ-4.2.1** [MAY] (Rec §2.3.1): Protocol clients may send update requests via the HTTP POST method by URL encoding the parameters.
- **REQ-4.2.2** [MUST] (Rec §2.3.1): When using this approach, clients shall URL percent-encode all parameters and include them as parameters within the request body via the `application/x-www-form-urlencoded` media type.
- **REQ-4.2.3** [MUST] (Rec §2.3.1): Parameters shall be separated with the ampersand (`&`) character.
- **REQ-4.2.4** [MAY] (Rec §2.3.1): Clients may include the parameters in any order.
- **REQ-4.2.5** [MUST] (Rec §2.3.1): The content type header of the HTTP request shall be set to `application/x-www-form-urlencoded`.

#### 4.3 Update via POST Directly
- **REQ-4.3.1** [MAY] (Rec §2.3.2): Protocol clients may send update requests via the HTTP POST method by including the update request directly and unencoded as the HTTP request message body.
- **REQ-4.3.2** [MUST] (Rec §2.3.2): When using this approach, clients shall include the SPARQL update request string, unencoded, and nothing else as the message body of the request.
- **REQ-4.3.3** [MUST] (Rec §2.3.2): Clients shall set the content type header of the HTTP request to `application/sparql-update`, with an optional `version` media-type parameter.
- **REQ-4.3.4** [MAY] (Rec §2.3.2): Clients may include the optional `using-graph-uri` and `using-named-graph-uri` parameters as HTTP query string parameters in the request URI.

#### 4.4 Update RDF Dataset Specification
- **REQ-4.4.1** [MAY] (Rec §2.3.3): The RDF Dataset for an update operation may be specified in the operation string itself using the `USING`, `USING NAMED`, and/or `WITH` keywords, or via the `using-graph-uri` and `using-named-graph-uri` parameters.
- **REQ-4.4.2** [MUST NOT]† (Rec §2.3.3): It is an error to supply the `using-graph-uri` or `using-named-graph-uri` parameters when conveying a SPARQL 1.2 Update request that contains an operation using the `USING`, `USING NAMED`, or `WITH` clause.
  > **Note:** The recommendation says "It is an error to supply" which is a standard W3C formulation for prohibition, though it does not use an explicit emphasized RFC 2119 keyword. The MUST NOT interpretation is well-established W3C practice.
- **REQ-4.4.3** [SHOULD]† (Rec §2.3.3): A SPARQL Update processor should treat each occurrence of the `using-graph-uri=g` parameter as if a `USING <g>` clause were included for every operation in the SPARQL 1.2 Update request.
  > **Note:** The recommendation uses non-emphasized "should".
- **REQ-4.4.4** [SHOULD]† (Rec §2.3.3): A SPARQL Update processor should treat each occurrence of the `using-named-graph-uri=g` parameter as if a `USING NAMED <g>` clause were included for every operation in the SPARQL 1.2 Update request.
  > **Note:** Same as REQ-4.4.3.

#### 4.5 Update Success Responses
- **REQ-4.5.1** [SHOULD] (Rec §2.3.4): A protocol service should use a `2XX` HTTP response code for an update request that is successfully processed.
- **REQ-4.5.2** [MAY] (Rec §2.3.4): A protocol service may choose instead to use a `3XX` response code as per HTTP.
- **REQ-4.5.3** [MAY] (Rec §2.3.4): The response body of a successful update request is implementation defined. Implementations may use HTTP content negotiation to provide both human-readable and machine-processable information about the completed update request.

#### 4.6 Update Failure Responses
- **REQ-4.6.1** [SHOULD]† (Rec §2.3.5): The service should return HTTP 400 if the SPARQL update request string is not a legal sequence of characters in the language defined by the SPARQL Update grammar.
  > **Note:** The recommendation introduces these with "The HTTP response code for an unsuccessful update request should be:" where "should" is not emphasized. Obligation level is inferred.
- **REQ-4.6.2** [SHOULD]† (Rec §2.3.5): The service should return HTTP 500 if the service fails to execute the update request. Services may also return a 500 response code if they refuse to execute an update request.
  > **Note:** Same as REQ-4.6.1.
- **REQ-4.6.3** [MAY] (Rec §2.3.5): The response body of a failed update request is implementation defined. Implementations may use HTTP content negotiation to provide human-readable or machine-processable (or both) information about the failed update request.
- **REQ-4.6.4** [MAY] (Rec §2.3.5): A protocol service may use other 4XX or 5XX HTTP response codes for other failure conditions, as per HTTP.

### 5. Base IRI Resolution

#### 5.1 Base IRI
- **REQ-5.1.1** [MUST] (Rec §2.4): The `BASE` keyword in a SPARQL query or update request string defines the Base IRI used to resolve relative IRIs per RFC 3986 section 5.1.1 ("Base URI Embedded in Content").
- **REQ-5.1.2** [MUST] (Rec §2.4): SPARQL Protocol services shall define their own base URI (per RFC 3986 section 5.1.4).
- **REQ-5.1.3** [MAY] (Rec §2.4): The service-defined base URI may be the service endpoint.

### 6. Response Formats

#### 6.1 Query Result Formats
- **REQ-6.1.1** [MUST]† (Rec §2.2, §2.2.6): For SELECT and ASK query forms, the service shall be capable of returning results in at least one of: SPARQL Results XML Format (`application/sparql-results+xml`), SPARQL Results JSON Format (`application/sparql-results+json`), or SPARQL Results CSV/TSV Formats (`text/csv`, `text/tab-separated-values`).
  > **Note:** The recommendation describes the response formats definitionally in §2.2 and §2.2.6 without a standalone RFC 2119 MUST for format support. The obligation is inferred from the structure of the specification.
- **REQ-6.1.2** [MUST]† (Rec §2.2, §2.2.6): For CONSTRUCT and DESCRIBE query forms, the service shall be capable of returning results as an RDF graph serialization (e.g., RDF/XML `application/rdf+xml`, Turtle `text/turtle`, or equivalent).
  > **Note:** Same as REQ-6.1.1.

## Non-Functional Requirements

### 7. Security and Policy

#### 7.1 Denial of Service Protection
- **REQ-7.1.1** [MAY] (Rec §4.1): A SPARQL protocol service may place restrictions on the resources that it retrieves or on the rate at which external resources are retrieved, to mitigate denial-of-service attacks from under-constrained queries or complex RDF Dataset descriptions.
- **REQ-7.1.2** [MAY] (Rec §4.1): SPARQL protocol services may log client requests to facilitate tracing with regard to third-party origin servers or services.
- **REQ-7.1.3** [MAY] (Rec §4.1): SPARQL protocol services may detect costly or otherwise unsafe queries, impose time or memory limits on queries, or impose other restrictions to reduce vulnerability to denial-of-service attacks.
- **REQ-7.1.4** [MAY] (Rec §4.1): SPARQL protocol services may refuse to process query requests that are deemed costly or unsafe.

#### 7.2 Update Security
- **REQ-7.2.1** [MAY]† (Rec §4.1): To protect against malicious or destructive updates, implementations may choose not to implement the update operation.
  > **Note:** The recommendation uses non-emphasized "may" in this paragraph.
- **REQ-7.2.2** [MAY]† (Rec §4.1): Implementations may choose to use HTTP authentication mechanisms or other implementation-defined mechanisms to prevent unauthorized invocations of the update operation.
  > **Note:** Same as REQ-7.2.1; non-emphasized "may".

#### 7.3 IRI Security
- **REQ-7.3.1** [SHOULD]† (Rec §4.1): Users and implementations should take care with IRIs that may have the same visual appearance but differ in character encoding (e.g., Cyrillic vs. Latin characters, combining characters), as described in Unicode Security Considerations (UTR #36) and RFC 3987 Section 8.
  > **Note:** The recommendation says "Users of SPARQL must take care" using non-emphasized "must". This requirements document uses SHOULD as the interpreted obligation level. The exact RFC 2119 level is ambiguous.

### 8. Conformance

#### 8.1 Conformant SPARQL Protocol Service
- **REQ-8.1.1** [MUST] (Rec §5.1): A conformant SPARQL Protocol service shall implement either the `query` operation or the `update` operation (or both) in the way described in the SPARQL 1.2 Protocol specification.
- **REQ-8.1.2** [MAY] (Rec §5.1): A conformant SPARQL Protocol service may implement both the `query` and `update` operations.
- **REQ-8.1.3** [MUST] (Rec §5.1): A conformant SPARQL Protocol service shall be consistent with the normative constraints (indicated by RFC 2119 keywords) described in Section 4 (Policy Considerations).

### 9. Internationalization

#### 9.1 Character Encoding
- **REQ-9.1.1** [MUST]† (Rec §2.2.3): For direct POST of queries (`application/sparql-query`), UTF-8 is the only valid charset.
  > **Note:** The recommendation explicitly states this for `application/sparql-query` in §2.2.3. However, the recommendation does **not** make an equivalent statement for `application/sparql-update` in §2.3.2. The previous version of this requirements document extended the UTF-8 requirement to updates; that extension is not supported by the recommendation text.
- **REQ-9.1.2** [MUST]† (Rec, normative references): The service shall support IRIs (Internationalized Resource Identifiers) as defined in RFC 3987 within queries and results.
  > **Note:** No explicit normative statement about IRI support exists in the recommendation text. This requirement is inferred from RFC 3987 being listed in the normative references and the use of IRIs throughout the SPARQL specifications.

## Analysis Notes

### A.1 RFC 2119 Keyword Convention

The recommendation's Document Conventions (§1.1) state: "When this document uses the words **must**, **must not**, **should**, **should not**, and **may**, and the words appear as emphasized text, they must be interpreted as described in [RFC2119]."

Throughout the recommendation, RFC 2119 keywords appear in two forms:
- `<strong>must</strong>`, `<strong>may</strong>`, etc. — in Sections 2, 4, and 5
- `<em class="rfc2119">MAY</em>` — only in Section 2.1 (Version Announcement)

Both forms qualify as "emphasized text." However, the recommendation also uses these words in non-emphasized (plain) text in several places. Per the Document Conventions, non-emphasized instances are not formal RFC 2119 keywords. Requirements in this document that are derived from non-emphasized instances are marked with a dagger (†).

This matters for conformance testing: a formal RFC 2119 MUST creates an unambiguous pass/fail criterion, while a plain-English "must" conveys normative intent but with less formal precision.

### A.2 Requirements Derived from Tables

Several requirements (REQ-3.1.3a, REQ-4.1.3a, REQ-3.3.0, REQ-4.2.0) are derived from constraints expressed in the summary tables of §2.2 and §2.3 (e.g., "version (0 or 1)", "None" for query string parameters) rather than from RFC 2119 keywords in prose. These tables are in normative sections and do express constraints, but the obligation levels (MUST NOT, SHOULD NOT) are editorial interpretations.

### A.3 UTF-8 Asymmetry Between Query and Update

The recommendation explicitly states that UTF-8 is the only valid charset for `application/sparql-query` (§2.2.3) but makes no equivalent statement for `application/sparql-update` (§2.3.2). This asymmetry may be an oversight in the recommendation rather than an intentional distinction, since both content types carry SPARQL text using the same Unicode character repertoire.

The former REQ-3.4.4a (MUST for UTF-8 encoding of query string parameters in POST-direct mode) and REQ-4.3.4a (SHOULD for UTF-8 encoding of query string parameters in update POST-direct mode) have been removed from this revision: the recommendation's UTF-8 note in §2.2.3 applies to the `application/sparql-query` content type as a whole, not specifically to query string parameter encoding, and §2.3.2 contains no parallel text.

### A.4 Empty Recommendation Sections

Sections C (Privacy Considerations), D (Security Considerations), and E (Internationalization Considerations) in the recommendation are currently stub sections marked "TODO". The security-related requirements in this document (Section 7) are derived from Rec §4.1 (Policy Considerations / Security), which is a separate normative section.

### A.5 ReSpec Conformance Boilerplate

The auto-generated conformance boilerplate in §5 mentions only "The key word MAY" (singular) as an RFC 2119 keyword, despite the recommendation using MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY throughout. This appears to be a ReSpec tooling artifact: the tool detected only the `<em class="rfc2119">MAY</em>` instances in §2.1 and did not count the `<strong>` keyword instances. This does not affect the normative force of the `<strong>` keywords, which are covered by the Document Conventions in §1.1.

### A.6 Conformance Section Numbering

The conformance section (§5.1) refers to "Section A.1: Normative References" and "Section A.2: Other References", but these sections are actually numbered G.1 and G.2 in the rendered document. Similarly, "Section 6: Changes" maps to Appendix A. This is a cosmetic issue in the recommendation, likely from the migration to ReSpec.

## Normative References

The following specifications are normatively referenced by the SPARQL 1.2 Protocol:

- **RDF12-CONCEPTS**: RDF 1.2 Concepts and Abstract Syntax
- **RDF12-TURTLE**: RDF 1.2 Turtle
- **RDF12-XML**: RDF 1.2 XML Syntax
- **RFC 2119**: Key words for use in RFCs to Indicate Requirement Levels
- **RFC 3986**: Uniform Resource Identifier (URI): Generic Syntax
- **RFC 3987**: Internationalized Resource Identifiers (IRIs)
- **RFC 8174**: Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words
- **RFC 9110**: HTTP Semantics
- **SPARQL12-GRAPH-STORE-PROTOCOL**: SPARQL 1.2 Graph Store Protocol
- **SPARQL12-QUERY**: SPARQL 1.2 Query Language
- **SPARQL12-RESULTS-CSV-TSV**: SPARQL 1.2 Query Results CSV and TSV Formats
- **SPARQL12-RESULTS-JSON**: SPARQL 1.2 Query Results JSON Format
- **SPARQL12-RESULTS-XML**: SPARQL 1.2 Query Results XML Format
- **SPARQL12-UPDATE**: SPARQL 1.2 Update
- **UTR36**: Unicode Security Considerations

## Changes from SPARQL 1.1 Protocol

The significant changes between SPARQL 1.1 Protocol and SPARQL 1.2 Protocol, as stated in Rec Appendix A, are:

- Added informative example of reified triples.
- Improved display on mobile phones.
- Added explicit references to RFCs.
- Used PREFIX instead of @prefix in all Turtle examples.

Additional changes identified by cross-referencing Sections 2.1, 3.1.14, and 3.1.15 of the recommendation:

- Added version announcement mechanism (`version` parameter and media-type parameter) for operations and responses (Rec §2.1).
- Updated normative references to RFC 9110 (HTTP Semantics), replacing older HTTP specifications.

## Requirements Summary

| Category | MUST | SHOULD | MAY | MUST NOT | SHOULD NOT | Total |
|---|---|---|---|---|---|---|
| HTTP Foundation | 2 | 0 | 0 | 0 | 0 | 2 |
| Version Announcement | 1 | 0 | 4 | 0 | 1 | 6 |
| Query Operation | 14 | 4 | 15 | 2 | 1 | 36 |
| Update Operation | 8 | 5 | 12 | 2 | 1 | 28 |
| Base IRI | 2 | 0 | 1 | 0 | 0 | 3 |
| Response Formats | 2 | 0 | 0 | 0 | 0 | 2 |
| Security / Policy | 0 | 1 | 6 | 0 | 0 | 7 |
| Conformance | 2 | 0 | 1 | 0 | 0 | 3 |
| Internationalization | 2 | 0 | 0 | 0 | 0 | 2 |
| **Total** | **33** | **10** | **39** | **4** | **3** | **89** |

Of these, 23 requirements (marked †) have obligation levels inferred from non-emphasized text or table constraints rather than explicit RFC 2119 keywords in the recommendation.

## Appendix B: Test-to-Requirement Mapping

This appendix provides the correct mapping between protocol test names (as defined in `sparql12.manifest.ttl`) and the requirements they validate. The manifest's `rdfs:comment` fields contain requirement references that use an incorrect numbering scheme inherited from earlier drafts. The corrected mapping is below.

### B.1 Corrected Test-to-Requirement Table

| Test | Manifest cites | Correct requirement(s) | Rationale |
|------|---------------|----------------------|-----------|
| bad_multiple_queries | REQ-3.2.1 | **REQ-3.1.2** | Tests that >1 query string is rejected. REQ-3.1.2 requires exactly one query. REQ-3.2.1 merely permits GET. |
| bad_multiple_updates | REQ-4.1.1 | **REQ-4.1.2** | Tests that >1 update string is rejected. REQ-4.1.2 requires exactly one update. REQ-4.1.1 merely requires POST. |
| bad_query_method | REQ-3.2.3 | **REQ-3.1.1** | Tests that PUT is rejected. REQ-3.1.1 requires GET or POST. REQ-3.2.3 is about ampersand separators. |
| bad_query_missing_direct_type | REQ-3.2.4 | **REQ-3.4.3** | Tests missing Content-Type for direct POST. REQ-3.4.3 requires `application/sparql-query`. REQ-3.2.4 is about parameter ordering. |
| bad_query_missing_form_type | REQ-3.2.4 | **REQ-3.3.5** | Tests missing Content-Type for form POST. REQ-3.3.5 requires `application/x-www-form-urlencoded`. REQ-3.2.4 is about parameter ordering. |
| bad_query_non_utf8 | REQ-3.2.6 | **REQ-3.4.5** | Tests non-UTF-8 encoding rejection. REQ-3.4.5 states UTF-8 is the only valid charset. **REQ-3.2.6 does not exist.** |
| bad_query_syntax | REQ-3.5.1 | **REQ-3.8.1** | Tests 4XX for invalid syntax. REQ-3.8.1 specifies HTTP 400 for illegal query. REQ-3.5.1 is about dataset specification. |
| bad_query_wrong_media_type | REQ-3.2.4 | **REQ-3.1.1a** | Tests wrong Content-Type rejection. REQ-3.1.1a requires parameters per defined options. REQ-3.2.4 is about parameter ordering. |
| bad_update_dataset_conflict | REQ-4.2.1 | **REQ-4.4.2** | Tests conflict between protocol params and USING/WITH. REQ-4.4.2 makes this an error. REQ-4.2.1 merely permits URL-encoded POST. |
| bad_update_form_body_missing | *(new)* | **REQ-4.2.2** | New test. URL-encoded POST with `update` param in query string instead of body. REQ-4.2.2 requires all params in the body. |
| bad_update_get | REQ-4.2.2 | **REQ-4.1.1** | Tests that GET is rejected for update. REQ-4.1.1 requires POST. REQ-4.2.2 is about URL encoding. |
| bad_update_missing_form_type | REQ-4.2.3 | **REQ-4.2.5** | Tests missing Content-Type for form update. REQ-4.2.5 requires `application/x-www-form-urlencoded`. REQ-4.2.3 is about ampersand separators. |
| bad_update_non_utf8 | REQ-4.2.4 | **(none exact)** | Tests non-UTF-8 for update. The recommendation does not explicitly require UTF-8 for `application/sparql-update` (see Analysis Note A.3). REQ-4.2.4 is about parameter ordering. By analogy, REQ-3.4.5 / REQ-9.1.1 apply. |
| bad_update_syntax | REQ-4.5.1 | **REQ-4.6.1** | Tests 4XX for invalid update syntax. REQ-4.6.1 specifies HTTP 400. REQ-4.5.1 is about *success* responses. |
| bad_update_wrong_media_type | REQ-4.2.3 | **REQ-4.1.1a** | Tests wrong Content-Type for update. REQ-4.1.1a requires params per defined options. REQ-4.2.3 is about ampersand separators. |
| query_content_type_ask | REQ-3.6.1 | **REQ-3.7.3, REQ-3.7.4** | Tests response Content-Type for ASK. REQ-3.7.3/3.7.4 specify response format. REQ-3.6.1 is about *client* content negotiation. |
| query_content_type_construct | REQ-3.6.1 | **REQ-3.7.3, REQ-3.7.4, REQ-6.1.2** | Tests response Content-Type for CONSTRUCT. |
| query_content_type_describe | REQ-3.6.1 | **REQ-3.7.3, REQ-3.7.4, REQ-6.1.2** | Tests response Content-Type for DESCRIBE. |
| query_content_type_select | REQ-3.6.1 | **REQ-3.7.3, REQ-3.7.4, REQ-6.1.1** | Tests response Content-Type for SELECT. |
| query_content_negotiation_xml | REQ-3.6.1 | **REQ-3.6.1** | Tests Accept header negotiation. Correct. |
| query_content_negotiation_json | REQ-3.6.1 | **REQ-3.6.1** | Tests Accept header negotiation. Correct. |
| query_dataset_default_graph | REQ-3.3.1 | **REQ-3.5.1** | Tests protocol-specified default graph. REQ-3.5.1 covers dataset specification. REQ-3.3.1 permits URL-encoded POST. |
| query_dataset_default_graphs_get | REQ-3.3.1 | **REQ-3.5.1** | Same as above. |
| query_dataset_default_graphs_post | REQ-3.3.1 | **REQ-3.5.1** | Same as above. |
| query_dataset_named_graphs_get | REQ-3.3.2 | **REQ-3.5.1** | Tests protocol-specified named graphs. REQ-3.5.1 covers dataset specification. REQ-3.3.2 is about URL encoding. |
| query_dataset_named_graphs_post | REQ-3.3.2 | **REQ-3.5.1** | Same as above. |
| query_dataset_full | REQ-3.3.1, REQ-3.3.2 | **REQ-3.5.1** | Tests both default and named graphs via protocol. |
| query_multiple_dataset | REQ-3.4.1 | **REQ-3.5.2** | Tests protocol-specified dataset overrides query-string dataset. REQ-3.5.2 specifies this. REQ-3.4.1 permits direct POST. |
| query_get | REQ-3.1.1, REQ-3.2.1 | **REQ-3.1.1, REQ-3.2.1** | Tests query via GET. Correct. |
| query_post_form | REQ-3.1.3, REQ-3.2.2 | **REQ-3.3.1, REQ-3.3.5** | Tests URL-encoded POST query. REQ-3.3.1 permits it, REQ-3.3.5 requires Content-Type. REQ-3.1.3 is about version; REQ-3.2.2 is about GET encoding. |
| query_post_direct | REQ-3.1.2, REQ-3.2.2 | **REQ-3.4.1, REQ-3.4.3** | Tests direct POST query. REQ-3.4.1 permits it, REQ-3.4.3 requires Content-Type. REQ-3.1.2 is about one query; REQ-3.2.2 is about GET encoding. |
| query_get_with_version | REQ-2.1.2, REQ-3.1.3 | **REQ-2.1.2, REQ-3.1.3** | Tests version parameter in GET. Correct. |
| query_post_direct_with_version_param | REQ-2.1.3 | **REQ-2.1.3, REQ-3.4.3** | Tests version media-type parameter. Correct (REQ-3.4.3 also relevant). |
| bad_query_multiple_versions | REQ-3.1.3a | **REQ-3.1.3a** | Tests >1 version rejected. Correct. |
| bad_update_multiple_versions | REQ-4.1.3a | **REQ-4.1.3a** | Tests >1 version rejected. Correct. |
| bad_query_get_with_body | REQ-3.2.5 | **REQ-3.2.5** | Tests GET with body rejected. Correct. |
| update_base_uri | REQ-5.1.1 | **REQ-5.1.1, REQ-5.1.2** | Tests service-defined base URI. Correct (REQ-5.1.2 also relevant). |
| update_dataset_default_graph | REQ-4.3.1 | **REQ-4.4.1, REQ-4.4.3** | Tests protocol-specified default graph for update. REQ-4.4.1/4.4.3 cover this. REQ-4.3.1 permits direct POST. |
| update_dataset_default_graphs | REQ-4.3.1 | **REQ-4.4.1, REQ-4.4.3** | Same as above. |
| update_dataset_full | REQ-4.3.1, REQ-4.3.2 | **REQ-4.4.1, REQ-4.4.3, REQ-4.4.4** | Tests both default and named graph params. |
| update_dataset_named_graphs | REQ-4.3.2 | **REQ-4.4.1, REQ-4.4.4** | Tests protocol-specified named graphs for update. REQ-4.3.2 is about unencoded body. |
| update_post_form | REQ-4.1.1, REQ-4.1.3 | **REQ-4.1.1, REQ-4.2.1** | Tests URL-encoded POST update. REQ-4.1.1 (POST required) correct. REQ-4.1.3 is about version; should be REQ-4.2.1 (permits URL-encoded). |
| update_post_direct | REQ-4.1.2, REQ-4.1.3 | **REQ-4.3.1, REQ-4.3.3** | Tests direct POST update. REQ-4.3.1 permits it, REQ-4.3.3 requires Content-Type. REQ-4.1.2 is about one update; REQ-4.1.3 is about version. |
| update_post_form_with_version | REQ-4.1.3, REQ-2.1.2 | **REQ-4.1.3, REQ-2.1.2** | Tests version in form-encoded update. Correct. |
| update_post_direct_with_version_param | REQ-2.1.3, REQ-4.3.3 | **REQ-2.1.3, REQ-4.3.3** | Tests version media-type param on update. Correct. |
| query_base_uri | REQ-5.1.1 | **REQ-5.1.1** | Tests BASE keyword resolution. Correct. |

### B.2 Summary of Manifest Errors

Of the original 45 tests, **27 had incorrect requirement references** in the manifest `rdfs:comment`. One new test (`bad_update_form_body_missing`) was added for REQ-4.2.2. The original errors fell into these categories:

1. **Off-by-section numbering** (22 tests): The manifest used requirement numbers from the wrong subsection. For example, dataset-related tests cited REQ-3.3.x (POST URL-encoded method) instead of REQ-3.5.x (dataset specification), and update dataset tests cited REQ-4.3.x (POST direct method) instead of REQ-4.4.x (dataset specification). This pattern suggests the manifest's numbering was based on a draft that used different section numbers.

2. **Non-existent requirement** (1 test): `bad_query_non_utf8` cites REQ-3.2.6 which does not exist. The correct requirement is REQ-3.4.5 (UTF-8 for `application/sparql-query`).

3. **Wrong semantic category** (4 tests): Some tests cite requirements about version or encoding when they should cite requirements about method or Content-Type (e.g., `update_post_form` cites REQ-4.1.3 about version instead of REQ-4.2.1 about URL-encoded POST).

### B.3 Corrected Requirement-to-Test Table

| Requirement | Tests |
|-------------|-------|
| REQ-2.1.2 | query_get_with_version, update_post_form_with_version |
| REQ-2.1.3 | query_post_direct_with_version_param, update_post_direct_with_version_param |
| REQ-3.1.1 | query_get, bad_query_method |
| REQ-3.1.1a | bad_query_wrong_media_type |
| REQ-3.1.2 | bad_multiple_queries |
| REQ-3.1.3 | query_get_with_version |
| REQ-3.1.3a | bad_query_multiple_versions |
| REQ-3.2.1 | query_get |
| REQ-3.2.5 | bad_query_get_with_body |
| REQ-3.3.1 | query_post_form |
| REQ-3.3.5 | query_post_form, bad_query_missing_form_type |
| REQ-3.4.1 | query_post_direct |
| REQ-3.4.3 | query_post_direct, query_post_direct_with_version_param, bad_query_missing_direct_type |
| REQ-3.4.5 | bad_query_non_utf8 |
| REQ-3.5.1 | query_dataset_default_graph, query_dataset_default_graphs_get, query_dataset_default_graphs_post, query_dataset_named_graphs_get, query_dataset_named_graphs_post, query_dataset_full |
| REQ-3.5.2 | query_multiple_dataset |
| REQ-3.6.1 | query_content_negotiation_xml, query_content_negotiation_json |
| REQ-3.7.3 | query_content_type_ask, query_content_type_construct, query_content_type_describe, query_content_type_select |
| REQ-3.7.4 | query_content_type_ask, query_content_type_construct, query_content_type_describe, query_content_type_select |
| REQ-3.8.1 | bad_query_syntax |
| REQ-4.1.1 | update_post_form, bad_update_get |
| REQ-4.1.1a | bad_update_wrong_media_type |
| REQ-4.1.2 | bad_multiple_updates |
| REQ-4.1.3 | update_post_form_with_version |
| REQ-4.1.3a | bad_update_multiple_versions |
| REQ-4.2.1 | update_post_form |
| REQ-4.2.2 | bad_update_form_body_missing |
| REQ-4.2.5 | bad_update_missing_form_type |
| REQ-4.3.1 | update_post_direct |
| REQ-4.3.3 | update_post_direct, update_post_direct_with_version_param |
| REQ-4.4.1 | update_dataset_default_graph, update_dataset_default_graphs, update_dataset_full, update_dataset_named_graphs |
| REQ-4.4.2 | bad_update_dataset_conflict |
| REQ-4.4.3 | update_dataset_default_graph, update_dataset_default_graphs, update_dataset_full |
| REQ-4.4.4 | update_dataset_full, update_dataset_named_graphs |
| REQ-4.6.1 | bad_update_syntax |
| REQ-5.1.1 | update_base_uri, query_base_uri |
| REQ-5.1.2 | update_base_uri |
| REQ-6.1.1 | query_content_type_select |
| REQ-6.1.2 | query_content_type_construct, query_content_type_describe |

### B.4 Requirements Without Dedicated Tests

The following requirements have no dedicated protocol test. For each, the rationale explains why a separate test is unnecessary.

| Requirement | Level | Description | Rationale |
|-------------|-------|-------------|-----------|
| REQ-3.2.2 | MUST | URL percent-encoding for GET parameters | Encoding correctness is a client obligation. Every GET test (query_get, query_dataset_default_graphs_get, etc.) exercises percent-encoded query strings; a server that rejected them would fail those tests. |
| REQ-3.2.3 | MUST | Ampersand separator between GET parameters | Same as REQ-3.2.2: multi-parameter GET tests (query_dataset_default_graphs_get, query_dataset_named_graphs_get) use `&`-separated params. |
| REQ-3.3.2 | MUST | URL encoding for POST form body | Same pattern: every form-encoded POST test (query_post_form, update_post_form, etc.) sends correctly encoded bodies. |
| REQ-3.4.4 | MAY | Clients may include `default-graph-uri` / `named-graph-uri` as query string params in direct POST | Implicitly demonstrated by `query_post_direct`, which sends `default-graph-uri` in the query string with `application/sparql-query` body. |
| REQ-3.5.3 | MAY | Service may reject client-specified dataset with HTTP 400 | Optional server-policy behaviour; not testable without knowledge of server configuration. |
| REQ-3.5.4 | MAY | Implementation-defined default dataset when none specified | Implementation-specific; no universal expected outcome to validate. |
| REQ-3.7.1, REQ-3.7.2 | SHOULD, MAY | 2XX/3XX for successful query | Every successful query test expects `ht:statusCodeValue "2XX", "3XX"`. |
| REQ-4.1.4 | MAY | Update requests may include zero or more `using-graph-uri` | Exercised by `update_dataset_default_graph`, `update_dataset_default_graphs`, and `update_dataset_full`, which pass `using-graph-uri` params. Covered by those tests' REQ-4.4.1/REQ-4.4.3 annotations. |
| REQ-4.1.5 | MAY | Update requests may include zero or more `using-named-graph-uri` | Exercised by `update_dataset_named_graphs` and `update_dataset_full`, which pass `using-named-graph-uri` params. Covered by those tests' REQ-4.4.1/REQ-4.4.4 annotations. |
| REQ-4.3.2 | MUST | Direct POST update body shall contain only the unencoded update string | Positive case demonstrated by `update_post_direct` (body is `CLEAR ALL`, nothing else). A negative test is impractical: extra content would make the body a syntactically invalid update, causing rejection under REQ-4.6.1 (bad syntax) rather than specifically REQ-4.3.2. |
| REQ-4.3.4 | MAY | Clients may include `using-graph-uri` / `using-named-graph-uri` as query string params in direct POST update | The upstream manifest tests this (its `update_dataset_*` tests use direct POST with dataset params in the query string). The sp12 manifest formulates those tests as form-encoded POST instead, so this specific combination is not independently exercised in sp12. |
| REQ-4.4.3, REQ-4.4.4 | SHOULD | `using-graph-uri` / `using-named-graph-uri` map to USING / USING NAMED clauses | Tested indirectly: `update_dataset_*` tests verify that protocol-specified dataset params produce the correct query results, which can only happen if the mapping is applied. |
| REQ-4.5.1, REQ-4.5.2 | SHOULD, MAY | 2XX/3XX for successful update | Every successful update test expects `ht:statusCodeValue "2XX", "3XX"`. |

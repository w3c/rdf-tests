<!-- SPDX-FileCopyrightText: 2026 Blackcat Informatics Inc. <paudley@blackcatinformatics.ca> -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Blank Triple Pattern proposals

These cases are proposed tests of SPARQL 1.2. Queries, RDF data and expected JSON results retain their independently reviewed source bytes. Expectations were derived from input graphs and normative algebra before implementation observations. No implementation output defines the oracle, and no adoption or universal engine conformance is claimed.

Compare the complete result header and multiset, preserving empty and all-unbound mappings. Blank labels permit one global bijection across the entire result, including repeated occurrences across rows and columns; independent per-row renaming is insufficient. Source documents and independent SERVICE result documents retain separate blank identity spaces. The SERVICE manifest uses standard `qt:serviceData` endpoint/data declarations; a test harness maps only declared endpoints to actual engines, with no arbitrary external endpoint access or canned expected response.

## Expectations

| Case | Kind | Independent derivation |
| --- | --- | --- |
| `quoted-pattern-blank` | query-evaluation | The existential inside the triple term denotes the same matched node as the outside r edge. There is one reported triple term, whose object is o. |

## Specification clauses

- <https://www.w3.org/TR/sparql12-query/#BGPsparqlBNodes>
- <https://www.w3.org/TR/sparql12-query/#syntaxNestedTriplePatterns>

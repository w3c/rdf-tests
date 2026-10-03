<!-- SPDX-FileCopyrightText: 2026 Blackcat Informatics Inc. <paudley@blackcatinformatics.ca> -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Algebra Interactions proposals

These cases are proposed tests of SPARQL 1.1. Queries, RDF data and expected JSON results retain their independently reviewed source bytes. Expectations were derived from input graphs and normative algebra before implementation observations. No implementation output defines the oracle, and no adoption or universal engine conformance is claimed.

Compare the complete result header and multiset, preserving empty and all-unbound mappings. Blank labels permit one global bijection across the entire result, including repeated occurrences across rows and columns; independent per-row renaming is insufficient. Source documents and independent SERVICE result documents retain separate blank identity spaces. The SERVICE manifest uses standard `qt:serviceData` endpoint/data declarations; a test harness maps only declared endpoints to actual engines, with no arbitrary external endpoint access or canned expected response.

## Expectations

| Case | Kind | Independent derivation |
| --- | --- | --- |
| `mixed-predicate-inverse-sequence` | query-evaluation | There is one direct t edge, one inverse q edge, and two p/r derivations through a and b. Each yields o, for exactly four copies. The wrong/r/other edge has no predecessor from s and cannot contribute. UNION and reordering basic patterns preserve this multiset; the middle witnesses are not projected. |
| `mixed-equivalent-union` | query-evaluation | There is one direct t edge, one inverse q edge, and two p/r derivations through a and b. Each yields o, for exactly four copies. The wrong/r/other edge has no predecessor from s and cannot contribute. UNION and reordering basic patterns preserve this multiset; the middle witnesses are not projected. |
| `mixed-permuted-union` | query-evaluation | There is one direct t edge, one inverse q edge, and two p/r derivations through a and b. Each yields o, for exactly four copies. The wrong/r/other edge has no predecessor from s and cannot contribute. UNION and reordering basic patterns preserve this multiset; the middle witnesses are not projected. |
| `mixed-overlapping-arm` | query-evaluation | The direct t and inverse q arms each yield one o. Both identical p/r arms yield two o. Alternative translation is UNION, so all six derivations remain; duplicate arms are not deduplicated. |
| `all-unbound-visible-rows` | query-evaluation | VALUES supplies two distinct local mappings. Projection names never, which is unbound in both; both empty visible bindings remain, and the declared never column remains even though no cell binds. |
| `duplicate-unbound-rows` | query-evaluation | The VALUES table contains two empty mappings. Bag cardinality is two and both declared columns are unbound. A grader that creates only edges for bound values would erase both rows and is invalid. |
| `bnode-fresh-per-call` | query-evaluation | Every argument-free BNODE invocation creates a fresh node. Two calls for each of two mappings produce four pairwise distinct blanks. The visible a/b keys identify each mapping, so independent per-row blank renaming cannot excuse cross-row aliasing. |
| `bnode-string-memo` | query-evaluation | In one solution mapping equal simple-literal BNODE arguments yield the same blank, so first equals again. Different literal a/b arguments and fresh argument-free calls produce four distinct identities across the two mappings. Equality must hold globally across the entire result bag, including repeated occurrences. |
| `global-blank-cycle` | query-evaluation | The source graph has two distinct blanks linked in both directions. There are exactly two rows and one global bijection: the from of one row is the to of the other. Four independently renamed nodes across the two rows are not equivalent. |

## Specification clauses

- <https://www.w3.org/TR/sparql11-query/#func-bnode>
- <https://www.w3.org/TR/sparql11-query/#sparqlAlgebra>
- <https://www.w3.org/TR/sparql11-query/#sparqlTranslatePathPatterns>

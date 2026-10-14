# Service Identity proposals

These cases are proposed tests of SPARQL 1.1. The query bodies, RDF statements and expected JSON results are unchanged from their independently reviewed sources. Expectations were derived from input graphs and normative algebra before implementation observations. No implementation output defines the oracle, and no adoption or universal engine conformance is claimed.

Compare the complete result header and multiset, preserving empty and all-unbound mappings. Blank labels permit one global bijection across the entire result, including repeated occurrences across rows and columns; independent per-row renaming is insufficient. Source documents and independent SERVICE result documents retain separate blank identity spaces. The SERVICE manifest uses standard `qt:serviceData` endpoint/data declarations; a test harness maps only declared endpoints to actual engines, with no arbitrary external endpoint access or canned expected response.

## Expectations

| Case | Kind | Independent derivation |
| --- | --- | --- |
| `service-bnode-distinct` | query-evaluation | The endpoint group yields one newly generated remote blank. The local p edge yields one existing blank; one local BNODE() invocation yields a fresh blank. The three identity classes are distinct, so the inequality filter preserves exactly one row with three distinct blanks. |
| `service-bnode-collision` | query-evaluation | The same one candidate mapping has three pairwise distinct blank identities. No equality disjunct holds, so the exact result bag is empty while the existing/local/remote header remains. |
| `service-response-shared` | query-evaluation | The endpoint contains one p subject and two distinct tag literals. There are exactly two mappings; both remote and copy denote that one subject in both rows. The result has one global blank class, not one independently renamed class per row. |
| `service-responses-distinct` | query-evaluation | The a and b endpoint files are separate RDF source documents independently parsed into distinct endpoint datasets. Each has one p subject. Each independently evaluated subquery yields one mapping; the join yields one pair of distinct source blanks, which passes the inequality filter. |
| `service-all-unbound-duplicates` | query-evaluation | The remote explicit SELECT projects a and b over a VALUES multiset containing two empty mappings. Projection preserves both mappings and both unbound header variables. The outer SERVICE join/projection therefore returns exactly two empty binding objects. |

## Specification clauses

- <https://www.w3.org/TR/2013/REC-sparql11-federated-query-20130321/>
- <https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#func-bnode>
- <https://www.w3.org/TR/2013/REC-sparql11-results-json-20130321/#select-encoding>

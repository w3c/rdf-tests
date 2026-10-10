# Scope Interactions proposals

These cases are proposed tests of SPARQL 1.1. The query bodies, RDF statements and expected JSON results are unchanged from their independently reviewed sources. Expectations were derived from input graphs and normative algebra before implementation observations. No implementation output defines the oracle, and no adoption or universal engine conformance is claimed.

Compare the complete result header and multiset, preserving empty and all-unbound mappings. Blank labels permit one global bijection across the entire result, including repeated occurrences across rows and columns; independent per-row renaming is insufficient. Source documents and independent SERVICE result documents retain separate blank identity spaces. The SERVICE manifest uses standard `qt:serviceData` endpoint/data declarations; a test harness maps only declared endpoints to actual engines, with no arbitrary external endpoint access or canned expected response.

## Expectations

| Case | Kind | Independent derivation |
| --- | --- | --- |
| `alternative-sequence` | query-evaluation | The p arm has witnesses a and b; the q arm has witness a. All three reach o. The disconnected wrong-to-other edge cannot join. |
| `repeated-alternatives` | query-evaluation | Each of two p witnesses matches two identical first arms and two identical second arms: 2 x 2 x 2 = 8 copies of o. |
| `inverse-sequence` | query-evaluation | Inverting the three legal derivations from s to o reverses the endpoints and preserves their three derivations. |
| `optional` | query-evaluation | s has three compatible right solutions. lonely has none and survives once with o unbound. |
| `minus-correlated` | query-evaluation | The right side shares s and removes s through compatibility; it has no row for lonely. |
| `minus-disjoint` | query-evaluation | The right relation is nonempty but shares no distinguished variable with the left. MINUS preserves all three left rows. |
| `exists` | query-evaluation | EXISTS tests presence once per outer row; three s witnesses do not multiply the single s row. |
| `not-exists` | query-evaluation | s has a compatible witness and is rejected; lonely has no witness and remains. |
| `subquery-hidden-name` | query-evaluation | The inner s is not projected, so it cannot join the outer s=lonely binding. The inner query independently emits three o rows. |
| `bind-values` | query-evaluation | Two identical VALUES rows each join three witnesses. BIND copies o into a distinguished column without changing the six-row bag. |
| `source-blank-connection` | query-evaluation | The same existential in one BGP connects its path endpoint to marker=yes, selecting only s and its three derivations. FILTER does not split the BGP. |
| `independent-union-blanks` | query-evaluation | Distinct existential labels in the two BGPs are legal and independent. p contributes a, b, dead; q contributes a. UNION preserves both copies of a. |
| `caller-lookalikes` | query-evaluation | Both legal user variable spellings remain distinguished and retain their literals for each of three path witnesses; translator names cannot capture them. |
| `zero-visible` | query-evaluation | Both endpoints are ground. Projecting all hidden witnesses leaves three copies of the empty solution, not one. |
| `distinct-zero-visible` | query-evaluation | The three projected empty solutions compare equal, so DISTINCT yields one empty row. |
| `distinct-visible` | query-evaluation | All three witnesses project to the same o binding and DISTINCT yields one row. |
| `illegal-union-label` | negative-syntax | A blank label occurs in two separate basic graph patterns; the source query must be rejected before execution. |
| `illegal-optional-label` | negative-syntax | A blank label occurs in two separate basic graph patterns; the source query must be rejected before execution. |
| `illegal-subquery-label` | negative-syntax | A blank label occurs in two separate basic graph patterns; the source query must be rejected before execution. |

## Specification clauses

- <https://www.w3.org/TR/sparql11-query/#BGPsparql>
- <https://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes>
- <https://www.w3.org/TR/sparql11-query/#OptionalMatching>
- <https://www.w3.org/TR/sparql11-query/#bind>
- <https://www.w3.org/TR/sparql11-query/#func-filter-exists>
- <https://www.w3.org/TR/sparql11-query/#inline-data>
- <https://www.w3.org/TR/sparql11-query/#modDuplicates>
- <https://www.w3.org/TR/sparql11-query/#neg-exists>
- <https://www.w3.org/TR/sparql11-query/#neg-minus>
- <https://www.w3.org/TR/sparql11-query/#neg-notexists>
- <https://www.w3.org/TR/sparql11-query/#select>
- <https://www.w3.org/TR/sparql11-query/#sparqlAlgebra>
- <https://www.w3.org/TR/sparql11-query/#sparqlTranslatePathPatterns>
- <https://www.w3.org/TR/sparql11-query/#subqueries>

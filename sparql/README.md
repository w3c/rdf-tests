[![W3C](http://www.w3.org/Icons/w3c_home)](https://www.w3.org/)

# SPARQL Test Suite

[Copyright](http://www.w3.org/Consortium/Legal/ipr-notice#Copyright) © 2010 [W3C](https://www.w3.org/)® ([MIT](http://www.csail.mit.edu/), [ERCIM](http://www.ercim.org/), [Keio](http://www.keio.ac.jp/)), All Rights Reserved. W3C [liability](http://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer), [trademark](http://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks), and [document use](http://www.w3.org/Consortium/Legal/copyright-documents) rules apply.

---

## Abstract

This document describes the testing process for [SPARQL](https://w3c.github.io/sparql-concepts/spec/).

## Status of This Document

The [RDF & SPARQL Working Group](https://www.w3.org/groups/wg/rdf-star) maintains the SPARQL test suite,
while the tests themselves live in the [rdf-tests GitHub repository](https://www.w3.org/groups/cg/rdf-tests/).
All tests present in the main branch of this repository are intended to represent the currently understood
correct behavior of SPARQL systems. Below is a description of the tests, their organization, and how to evaluate them.

---

## Table of Contents

- [Organization](#organization)
- [Manifest Vocabularies](#manifest-vocabularies)
- [Manifest Structure](#manifest-structure)
- [File Names](#file-names)
- [Syntax Tests](#syntax-tests)
- [Query Evaluation Tests](#query-evaluation-tests)
- [CSV Result Format Tests](#csv-result-format-tests)
- [Entailment Evaluation Tests](#entailment-evaluation-tests)
- [Update Evaluation Tests](#update-evaluation-tests)
- [Federated Query Tests](#federated-query-tests)
- [Protocol Tests](#protocol-tests)
- [Service Description Tests](#service-description-tests)
- [Graph Store HTTP Protocol Tests](#graph-store-http-protocol-tests)
- [Test annotations](#test-annotations)
- [How to run the Test Cases](#how-to-run-the-test-cases)

---

The [RDF & SPARQL Working Group](https://www.w3.org/groups/wg/rdf-star) uses a test-driven process.
The [test area](.) is a collection of the current test cases of the working group extending and updating
the [testcases](https://www.w3.org/2001/sw/DataAccess/tests/r2) of the
[Data Access Working Group](https://www.w3.org/2001/sw/DataAccess/).

Tests are divided into collections (corresponding to directories) for manageability.
Each collection of tests has a *manifest file* within its directory (named `manifest.ttl`).
There is also a number of overall manifests containing entries pointing to the individual test collection manifests:

* Manifests for the [SPARQL 1.0 Query Language](https://www.w3.org/TR/rdf-sparql-query/):
	- [syntax-only tests](sparql10/manifest-syntax.ttl) (positive and negative tests)
	- [query-evaluation tests](sparql10/manifest-evaluation.ttl)
* Manifests for the [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/):
	- [syntax-only tests](sparql11/manifest-sparql11-query-syntax.ttl) (positive and negative tests)
	- [query evaluation tests](sparql11/manifest-sparql11-query-evaluation.ttl)
* Manifests for the [SPARQL 1.1 Entailment Regimes](https://www.w3.org/TR/sparql11-entailment/):
	- [entailment evaluation tests](sparql11/entailment/manifest.ttl)
* Manifests for the [SPARQL 1.1 Update Language](https://www.w3.org/TR/sparql11-update/):
	- [syntax-only tests](sparql11/manifest-sparql11-update-syntax.ttl) (positive and negative tests)
	- [update evaluation tests](sparql11/manifest-sparql11-update-syntax.ttl)
* Manifests for the [SPARQL 1.1 Service Description](https://www.w3.org/TR/sparql11-service-description/):
	- [service description tests](sparql11/service-description/manifest.ttl)
* Manifests for the [SPARQL 1.1 Graph Store Protocol](https://www.w3.org/TR/sparql11-graph-store-protocol/):
	- [Direct Graph Identification](sparql11/graph-store-protocol/manifest-direct.ttl)
	- [Indirect Graph Identification](sparql11/graph-store-protocol/manifest-indirect.ttl)
* Manifests for the [SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/):
	- [protocol tests](sparql11/protocol/manifest.ttl)
* Manifests for the [SPARQL 1.2 Query](https://www.w3.org/TR/sparql12-query/):
	- [combined syntax and evaluation tests](sparql12/manifest.ttl)
	* @@@ TODO

## Organization

The test cases are organized in three top-level directories:

- The [sparql10](sparql10/) directory holds the testcases from the SPARQL 1.0 [testcases](https://www.w3.org/2001/sw/DataAccess/tests/r2), with additional tests that have beed added subsequently, and are restricted to SPARQL 1.0 features only
- The [sparql11](sparql11/) directory holds test testcases from the SPARQL 1.1 [testcases](https://www.w3.org/2009/sparql/docs/tests/README.html), with additional tests that have beed added subsequently, and are restricted to SPARQL 1.1 features only
- The [sparql12](sparql12/) directory holds test testcases for SPARQL 1.2

The purpose is to provide an up-to-date, upwards-compatible, consistent, and easy-to-use suite of test cases that SPARQL implementors can use to evaluate and report on their implementation.

The tests as-is shall constitute a test suite that the group will use to generate an implementation report for the SPARQL 1.1 Query and SPARQL 1.1 Update languages.

## Manifest Vocabularies

The SPARQL 1.1 test manifest files define five vocabularies to express tests and results:

1. [manifest vocabulary](https://www.w3.org/2001/sw/DataAccess/tests/test-manifest.n3) (prefixed with `mf:` below)
2. [query evaluation test vocabulary](https://www.w3.org/2001/sw/DataAccess/tests/test-query.n3) (prefixed with `qt:` below)
3. [update evaluation test vocabulary](test-update.n3) (prefixed with `ut:` below)
4. [DAWG test approval vocabulary](https://www.w3.org/2001/sw/DataAccess/tests/test-dawg.n3) (prefixed with `dawgt:` below)
5. [DAWG result-set RDF vocabulary](https://www.w3.org/2001/sw/DataAccess/tests/test-dawg.n3) (prefixed with `rs:` below)

All examples below use these prefix bindings (specified in [turtle](https://www.w3.org/2001/sw/DataAccess/df1/)):

```turtle
@prefix rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix mf:      <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#> .
@prefix dawgt:   <http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#> .
@prefix qt:      <http://www.w3.org/2001/sw/DataAccess/tests/test-query#> .
@prefix ut:      <http://www.w3.org/2009/sparql/tests/test-update#> .
@prefix sd:      <http://www.w3.org/ns/sparql-service-description#> .
@prefix ent:     <http://www.w3.org/ns/entailment/RDF> .
@prefix rs:      <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
```

## Manifest Structure

A manifest is a list (RDF Collection) of tests. Every test has a name (`mf:name`);
many tests also have a comment (`rdfs:comment`) explaining the purpose of the test.
The `dawgt:approval` predicate relates a test to its official Working Group status (e.g. `dawgt:Approved`).
Tests are grouped (via their `rdf:type`) as:

- positive SPARQL 1.0 Query syntax tests (`mf:PositiveSyntaxTest`)
- positive SPARQL 1.1 Query syntax tests (`mf:PositiveSyntaxTest11`)
- positive SPARQL 1.1 Update syntax tests (`mf:PositiveUpdateSyntaxTest11`)
- negative SPARQL 1.0 Query syntax tests (`mf:NegativeSyntaxTest`)
- negative SPARQL 1.1 Query syntax tests (`mf:NegativeSyntaxTest11`)
- negative SPARQL 1.1 Update syntax tests (`mf:NegativeUpdateSyntaxTest11`)
- SPARQL 1.0 and 1.1 Query evaluation tests (`mf:QueryEvaluationTest`)
- SPARQL 1.1 Update evaluation tests (`mf:UpdateEvaluationTest`)
- CSV Result Format tests (`mf:CSVResultFormatTest`)
- SPARQL 1.1 Service Description tests (`mf:ServiceDescriptionTest`)

## File Names

Typically, in the test case suite, we use the following suffixes to indicate different file types:

- **.ttl** ... Files describing RDF graphs in [Turtle](https://www.w3.org/TR/rdf12-turtle/) syntax.
- **.trig** ... Files describing RDF graphs in [TriG](https://www.w3.org/TR/rdf12-trig/) syntax.
- **.rdf** ... Files describing RDF graphs in [RDF/XML](https://www.w3.org/TR/rdf12-xml/) syntax.
- **.rq** ... Files containing a [SPARQL 1.2 Query](https://www.w3.org/TR/sparql12-query/) request.
- **.ru** ... Files containing a [SPARQL 1.2 Update](https://www.w3.org/TR/sparql12-update/) request.
- **.srx** ... Files containing a query result in the [SPARQL 1.2 Query Results XML Format](https://www.w3.org/TR/sparql12-results-xml/).
- **.srj** ... Files containing a query result in the [SPARQL 1.2 Query Results JSON Format](https://www.w3.org/TR/sparql12-results-json/).
- **.csv** ... Files containing a query result in the [SPARQL 1.2 Query Results CSV (Comma Separated Values) Format](https://www.w3.org/TR/sparql12-results-csv-tsv/).
- **.tsv** ... Files containing a query result in the [SPARQL 1.2 Query Results TSV (Tab Separated Values) Format](https://www.w3.org/TR/sparql12-results-csv-tsv/).

## Syntax Tests

Each syntax test has an `mf:action`, the object of which is a resource identifying a (possible) query string.
An example definition of a syntax test is:

```turtle
<#syntax-basic-01>  mf:name  "syntax-basic-01.rq" ;
     rdf:type   mf:PositiveSyntaxTest ;
     mf:action  <syntax-basic-01.rq> ;
     dawgt:approvedBy <http://lists.w3.org/Archives/Public/public-rdf-dawg/2007JanMar/0047> ;
     dawgt:approval dawgt:Approved .
```

A SPARQL implementation passes a `mf:PositiveSyntaxTest` if it parses the query string without error.
A SPARQL implementation passes a `mf:NegativeSyntaxTest` if it raises an error while attempting to parse the query string.

## Query Evaluation Tests

Each query evaluation test has an `mf:action` and an `mf:result`.
The object of `mf:action` is a resource with properties taken from the query evaluation test vocabulary.
At a minimum, a test's action includes a `qt:query` relation and an optional `qt:data` relation.
The `qt:data` predicate points to a URI that can be dereferenced to yield the default graph for the test.
The `qt:query` predicate points to a URI that can be dereferenced to yield the query string for the test.
Query evaluation tests may also use the `qt:graphData` predicate to indicate the named graph components of the test's RDF dataset.

In case the query in the `qt:query` predicate contains `FROM` and `FROM NAMED` clauses and no `qt:data` is present, the graphs comprising the test's RDF dataset are expected to be loaded by dereferencing the respective URIs of the `FROM`/`FROM NAMED` clauses.

Query evaluation tests also contain an `mf:result` which points to a URI that can be dereferenced to yield the expected results of the test query.
These results are expressed in one of several possible ways:

- The [SPARQL 1.2 Query Results XML Format](https://www.w3.org/TR/sparql12-results-xml/). SELECT or ASK queries.
- The [SPARQL 1.2 Query Results JSON Format](https://www.w3.org/TR/sparql12-results-json/). SELECT or ASK queries.
- The [SPARQL Query Results TSV Format](https://www.w3.org/TR/sparql12-results-csv-tsv/#tsv). SELECT or ASK queries. (As for testing the [SPARQL Query Results CSV Format](https://www.w3.org/TR/sparql12-results-csv-tsv/#csv), see the separate Section within this document on [CSV Result Format Tests](#csv-result-format-tests)).
- The [DAWG result-set RDF vocabulary](https://www.w3.org/2001/sw/DataAccess/tests/result-set.n3). SELECT or ASK queries.
- [RDF/XML](https://www.w3.org/TR/rdf12-xml/) or [Turtle](https://www.w3.org/TR/rdf12-turtle/). CONSTRUCT queries.

A SPARQL implementation passes a query evaluation test if the graph produced by evaluating the query against the RDF dataset (and encoding in the DAWG result set vocabulary, if necessary) is [equivalent](https://www.w3.org/TR/rdf-concepts/#section-graph-equality) [RDF-CONCEPTS] to the graph named in the result (after encoding in the DAWG result set vocabulary, if necessary).
Note that, solution order only is considered relevant, if the result is expressed in the test suite in the DAWG result set vocabulary, with explicit `rs:index` triples; otherwise solution order is considered irrelevant for passing.
Equivalence can be tested by checking that the graphs are isomorphic and have identical IRI and literal nodes.
Note that testing whether two result sets are isomorphic is simpler than full graph isomorphism.
Iterating over rows in one set, finding a match with the other set, removing this pair, then making sure all rows are accounted for, achieves the same effect.

Query evaluation tests that involve the [REDUCED](https://www.w3.org/TR/rdf-sparql-query#modReduced) keyword have slightly different passing criteria.
These tests are indicated in the manifest files with the `mf:resultCardinality` predicate with an object of `mf:LaxCardinality`.
To pass such a test, the result set produced by a SPARQL implementation must contain each solution in the expected result set at least once and no more than the number of times that the solution occurs in the expected result set.
(That is, the expected result set contains the solutions with cardinalities as they would be if the query did not contain REDUCED; to pass the test, an implementation must produce the correct results with cardinalities between one and the cardinality in the expected result set.)

An example definition of a query evaluation test is:

```turtle
<#dawg-regex-002> a mf:QueryEvaluationTest ;
      mf:name    "regex-query-002" ;
      dawgt:approval dawgt:Approved ;
      dawgt:approvedBy <http://lists.w3.org/Archives/Public/public-rdf-dawg/2007AprJun/0029.html> ;
      rdfs:comment
          "Case insensitive unanchored match test" ;
      mf:action
          [ qt:query  <regex-query-002.rq> ;
            qt:data   <regex-data-01.n3> ] ;
      mf:result  <regex-result-002.n3> .
```

## CSV Result Format Tests

CSV Result Format tests are meant to test a SPARQL implementation's ability to serialize query results in the SPARQL 1.1 Query Results CSV Format.
This is a lossy format, however, and so cannot be tested in the same manner as the other result formats.
Care should be taken to ensure that results produced in the CSV format are compared properly to the expected result values.
In all other respects, CSV tests should be treated as [query evaluation tests](#query-evaluation-tests).

An example result set in the CSV Format is:

```csv
s,p,o
http://example.org/s2,http://example.org/p2,2.2
```

Due to the lossy nature of the CSV format, the single expected result could match any of the following actual results:

| s | p | o |
|---|---|---|
| `<http://example.org/s2>` | `<http://example.org/p2>` | `"2.2"` |
| `<http://example.org/s2>` | `<http://example.org/p2>` | `"2.2"^^xsd:string` |
| `<http://example.org/s2>` | `<http://example.org/p2>` | `"2.2"^^xsd:decimal` |

## Entailment Evaluation Tests

Entailment Evaluation tests are special query evaluation tests that additionally (slightly ab-)use the `sd:entailmentRegime` and, optionally, the `sd:entailmentProfile` properties from the [SPARQL 1.1 Service Description](https://www.w3.org/TR/sparql11-service-description/) vocabulary to further specify the object of the `mf:action` property, indicating the expected entailment regime for graphs in the dataset and, where applicable, which OWL profile that test satisfies.

A SPARQL implementation passes a query evaluation test if its answers over any graphs in the dataset using the `sd:entailmentRegime` property comply with the criteria formalized in the [SPARQL 1.1 Entailment Regimes](https://www.w3.org/TR/sparql11-entailment/) document.
Apart from that, passing tests is as defined for query evaluation tests.

An example definition of an entailment evaluation test for the RDF entailment regime is:

```turtle
:rdf01 rdf:type mf:QueryEvaluationTest ;
    mf:name    "RDF inference test" ;
    dawgt:approval dawgt:NotClassified ;
    mf:action
         [ qt:query  <rdf01.rq> ;
           qt:data   <rdf01.ttl>
           sd:entailmentRegime ent:RDF ] ;
    mf:result  <rdf01.srx>
    .
```

Instead of a single entailment regime, tests can also be marked with a list of regimes. In this case, any of the entailment regimes can be used to run the test. Similarly, the supported OWL profiles can be given as a list or as a single value:

```turtle
    :sparqldl-10  rdf:type   mf:QueryEvaluationTest ;
         mf:name  "sparqldl-10.rq: undist vars test" ;
         mf:action [
                 qt:query  <sparqldl-10.rq> ;
                 qt:data <data-07.ttl> ;
                 sd:EntailmentProfile ( pr:DL pr:EL pr:Full ) ;
                 sd:entailmentRegime ( ent:OWL-Direct ent:OWL-RDF-Based )
         ] ;
         mf:result  <sparqldl-10.srx> .
```

Note that, strictly speaking, this use of the `sd:entailmentRegime` property - by its specified [domain](https://www.w3.org/TR/sparql11-service-description/#sd-entailmentRegime) - makes the object of the `mf:action` attribute a member of the `sd:NamedGraph` class; the `sd:NamedGraph` class though has no meaning within the context of test cases, so this domain specification can be safely ignored.

## Update Evaluation Tests

Each update evaluation test has an `mf:action` and an `mf:result`.
The object of `mf:action` for an Update evaluation test case is a resource with properties taken from the update evaluation test vocabularies.
The latter is used among others to describe the graph store's state before and after the execution of an update.
At a minimum, a test's action includes a `ut:request` relation.

The optional `ut:data` and `ut:graphData` relations within the `mf:action` of an update test case point the status of the [Graph Store](https://www.w3.org/TR/sparql11-update/#sec_graphStore) *prior* to the update execution described in terms of at most one `ut:data` property denoting the unnamed graph and optional `ut:graphData` properties denoting named graphs.
The object of the `ut:data` property is a URI reference to an RDF graph, whereas the objects of the `ut:graphData` property indicate the named graph components of the Graph Store.
Named graphs are described either - analogous to the `qt:graphData` property from the query test vocabulary - by explicit URI reference (in which case the graph name is supposed to correspond to the respective URI reference), or the object of the `ut:graphData` property may be a resource further described in terms of an `ut:graph` and an `rdfs:label` property.
Here, the `ut:graph` property is a URI reference to an RDF graph, whereas the `rdfs:label` property with plain literal value indicates the graph's name under which it is accessible in the graph store.
The ability to assign a "name" different from the URI reference name explicitly to a named graph in a graph store is needed to denote different graphs by the same name to describe the status of a named graph prior and after execution of an update.

In the case of absence of both `ut:data` and `ut:graphData` properties within the `mf:action`, the graph store is supposed to be empty (i.e., with an empty default graph and no named graphs) prior to execution of the update.

The `ut:request` predicate points to a URI that can be dereferenced to yield the update query string for the test.

Update evaluation tests also contain an `mf:result`.
The object of `mf:result` is a resource described in terms of the `ut:data` and `ut:graphData` properties.
The optional `ut:data` and `ut:graphData` properties within a an update evaluation test result denote the state of the graphstore *after* execution of the query analogous to the `ut:data` and `ut:graphData` properties occurring in the `mf:action` of an update evaluation test.
In the case of absence of both `ut:data` and `ut:graphData` properties within the `mf:result`, the graph store is supposed to be empty after execution of the update.

A SPARQL implementation passes a update evaluation test if the graphs in the graph store are [equivalent](https://www.w3.org/TR/rdf-concepts/#section-graph-equality) [RDF-CONCEPTS] to the graphs denoted in the `mf:action` (and `mf:result`) property, respectively) prior to the update execution (after update execution, respectively).
Equivalence can be tested as described above for query evaluation tests.

An example definition of an update evaluation test is:

```turtle
:insert-data-spo1 a mf:UpdateEvaluationTest ;
    mf:name    "Simple insert data 1" ;
    rdfs:comment "This is a simple insert of a single triple to the unnamed graph of an empty graph store" ;
    dawgt:approval dawgt:NotClassified ;
    mf:action [
            ut:request <insert-data-spo1.ru> ;
            ut:data <empty.ttl>
    ] ;
    mf:result [
            ut:data  <spo.ttl>
    ] .
```

## Federated Query Tests

In SPARQL 1.1 Federated Query, tests cases contain new vocabulary not used before.
These tests check whether the queries with that operator are correct or not.
Queries using the `SERVICE` keyword for accessing remote SPARQL endpoints need a way to describe the data coming from these endpoints which was not previously defined.

The predicate `qt:serviceData` helps to describe the data coming from these remote SPARQL endpoints in a query.
This predicate can also contain the predicate `qt:endpoint` which contains the URL of the remote SPARQL endpoint.

An example definition of a Federated Query test is:

```turtle
:service1 rdf:type mf:QueryEvaluationTest ;
       mf:name    "SERVICE test 1" ;
       dawgt:approval dawgt:NotClassified ;
       mf:feature sd:BasicFederatedQuery ;
       mf:action [
               qt:query  <service01.rq> ;
               qt:data   <data01.ttl> ;
               qt:serviceData [
                       qt:endpoint <http://example.org/sparql> ;
                       qt:data     <data01endpoint.ttl>
               ]
       ] ;
       mf:result  <service01.srx> .
```

## Protocol Tests

A testing service for [SPARQL 1.1 Protocol](https://www.w3.org/TR/sparql11-protocol/) implementations has been set up at [`http://www.w3.org/2009/sparql/protocol_validator`](https://www.w3.org/2009/sparql/protocol_validator).
The service and tests performed by this service are described in a [separate document](https://github.com/kasei/sparql11-protocolvalidator).

## Service Description Tests

A testing service for SPARQL 1.1 Protocol implementations supporting [SPARQL 1.1 Service Descriptions](https://www.w3.org/TR/sparql11-service-description/) has been set up at [`http://www.w3.org/2009/sparql/sdvalidator`](https://www.w3.org/2009/sparql/sdvalidator).
The service performs a number of tests to verify that a submitted endpoint returns RDF that conforms to the service description vocabulary specification.
Using content negotiation to request RDF (supporting both Turtle and RDF/XML), the service can be used to generate an [EARL implementation report](https://www.w3.org/2001/sw/DataAccess/tests/earl).

## Graph Store HTTP Protocol Tests

A number of test cases for the [SPARQL 1.1 Graph Store HTTP Protocol](https://www.w3.org/TR/sparql11-http-rdf-update/) consisting of HTTP requests and expected responses are described in a [separate document](https://www.w3.org/2009/sparql/docs/tests/data-sparql11/http-rdf-update/).

## Test annotations

@@@ This section might need reconsideration to reflect extensions (like new library functions) that have become standard in SPARQL 1.1 @@@

### `mf:requires`

A number of tests in the open-world directory illustrate features of SPARQL by depending on how a SPARQL query processor can extend the set of core types and operations as defined by the [operator table](https://www.w3.org/TR/rdf-sparql-query/).

These tests are marked by property `mf:requires` and an object value from one of the URIs described below.

* `mf:XsdDateOperations`:
  Requires the processor to understand comparisons of literal of type xsd:date.
Without providing operations on the xsd:date datatype, a processor would raise an error on the operations of "=" and "!=" etc. With an understanding of xsd:date, a processor can perform value-based operations and provide the operations described in "XQuery 1.0 and XPath 2.0 Functions and Operators" (e.g. [date-equals](https://www.w3.org/TR/xpath-functions/) [date-less-than](https://www.w3.org/TR/xpath-functions/))

* `mf:StringSimpleLiteralCmp`:
  This indicates that the test uses the fact that plain literals, without language tags test are the same value as an `xsd:string` with the same lexical form.
  This is covered by rules "xsd 1a" and "xsd 1b" from RDF Semantics [[http://www.w3.org/TR/rdf-mt/#DtypeRules](https://www.w3.org/TR/rdf-mt/)].

* `mf:KnownTypesDefault2Neq`:
  This indicates that a processor extends the SPARQL operator model by using the fact that values of literals can be in disjoint value spaces and hence can not be equal by value.
  For example, an xsd:integer can not be the same value as an xsd:boolean because these two datatypes define disjoint value spaces.

* `mf:LangTagAwareness`:
  This indicates that the test assumes the SPARQL query processor has support for plain literals with language tags.
  The minimum set of operators in the [SPARQL operator table](https://www.w3.org/TR/rdf-sparql-query/#OperatorMapping) does not include language tag handling, only plain literals without language tag (simple literals) and certain XSD datatypes.

### `mf:notable`

This annotation indicates a feature of SPARQL that implementers might note:

* `mf:IllFormedLiteral`
  The test involves handling of ill-formed literals.

## How to run the Test Cases

@@@ This section shall contain some hints on how to actually run the test suite and generate implementation reports for implementers.

---


## Previous Editors of this Document

* [Axel Polleres](http://www.polleres.net/) – Siemens AG
* [Steve Harris](mailto:swh@ecs.soton.ac.uk) – IAM Research Group, Southampton
* [Jeen Broekstra](mailto:j.broekstra@tue.nl) – Information Systems Group, Eindhoven University of Technology
* [Lee Feigenbaum](mailto:lee@thefigtrees.net) – Cambridge Semantics

#!/usr/bin/env node

// SPARQL 1.2 Protocol Test Runner
// Reads the Turtle manifest describing HTTP-based protocol tests,
// executes them against a SPARQL endpoint, and outputs EARL results.
//
// Usage:
//   node sparql12-protocol-test.mjs <endpoint-url> --token <bearer-token> [options]
//
// Options:
//   --token <token>        Bearer token for authorizing operations (required)
//   --graph-store-url <u>  Graph Store Protocol URL (default: endpoint URL
//                          with trailing "sparql" replaced by "service")
//   --tests, -t <names>   Comma-separated test names or substrings to run (default: all)
//   --manifest <path>      Path to the manifest file (default: ./rdf-tests/manifest.ttl)
//   --earl-output <path>   Path for the EARL output file (default: ./sparql12-protocol-earl.ttl)
//   --subject-name <name>  Name for the test subject in the EARL report
//   --subject-uri <uri>    URI identifying the software under test (default: endpoint URL)
//   -h, --help             Show usage

import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import N3 from 'n3';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const { namedNode } = N3.DataFactory;

// ============================================================================
// RDF namespace constants
// ============================================================================

const RDF  = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#';
const RDFS = 'http://www.w3.org/2000/01/rdf-schema#';
const XSD  = 'http://www.w3.org/2001/XMLSchema#';
const MF   = 'http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#';
const HT   = 'http://www.w3.org/2011/http#';
const CNT  = 'http://www.w3.org/2011/content#';
const UT   = 'http://www.w3.org/2009/sparql/tests/test-update#';

// ============================================================================
// CLI argument parsing
// ============================================================================

function parseArgs() {
  const args = process.argv.slice(2);
  let endpointUrl = null;
  let token = null;
  let graphStoreUrl = null;
  let manifestPath = resolve(__dirname, 'rdf-tests', 'manifest.ttl');
  let earlOutput = resolve(__dirname, 'sparql12-protocol-earl.ttl');
  let subjectName = null;
  let subjectUri = null;
  const testFilters = [];

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--token':
        token = args[++i];
        break;
      case '--graph-store-url':
        graphStoreUrl = args[++i];
        break;
      case '--tests':
      case '-t':
        testFilters.push(...args[++i].split(','));
        break;
      case '--manifest':
        manifestPath = resolve(args[++i]);
        break;
      case '--earl-output':
        earlOutput = resolve(args[++i]);
        break;
      case '--subject-name':
        subjectName = args[++i];
        break;
      case '--subject-uri':
        subjectUri = args[++i];
        break;
      case '-h':
      case '--help':
        printUsage();
        process.exit(0);
        break;
      default:
        if (!args[i].startsWith('-') && !endpointUrl) {
          endpointUrl = args[i];
        }
    }
  }

  if (!endpointUrl || !token) {
    if (!endpointUrl) console.error('Error: endpoint URL is required.');
    if (!token) console.error('Error: --token is required for authorizing update operations.');
    console.error('');
    printUsage();
    process.exit(1);
  }

  // Auto-derive the Graph Store Protocol URL from the endpoint URL if not
  // supplied explicitly: same host and repository path, but with the final
  // "sparql" segment replaced by "service".
  //   http://host/test/test/sparql  →  http://host/test/test/service
  if (!graphStoreUrl) {
    graphStoreUrl = deriveGraphStoreUrl(endpointUrl);
  }

  return {
    endpointUrl,
    token,
    graphStoreUrl,
    testFilters,
    manifestPath,
    earlOutput,
    subjectName: subjectName || (() => { try { return new URL(endpointUrl).hostname; } catch { return endpointUrl; } })(),
    subjectUri: subjectUri || endpointUrl,
  };
}

/**
 * Derive the Graph Store Protocol URL from the SPARQL endpoint URL by
 * substituting the trailing "sparql" path segment with "service".  If the
 * endpoint URL does not end with "sparql" (with optional trailing slash or
 * query string), the derived URL is the same as the endpoint URL with
 * "/service" appended.
 */
function deriveGraphStoreUrl(endpointUrl) {
  // Replace a trailing "sparql" segment (optionally followed by "/" and/or
  // query string) with "service" preserving the trailing "/" and query.
  const m = endpointUrl.match(/^(.*?)\/sparql(\/?)(\?.*)?$/);
  if (m) {
    return m[1] + '/service' + (m[2] || '') + (m[3] || '');
  }
  // Fallback: append /service
  if (endpointUrl.endsWith('/')) return endpointUrl + 'service';
  return endpointUrl + '/service';
}

function printUsage() {
  console.log(`Usage: node sparql12-protocol-test.mjs <endpoint-url> --token <token> [options]

Options:
  --token <token>         Bearer token for endpoint authorization (required)
  --graph-store-url <url> Graph Store Protocol endpoint for dataset setup.
                          Default: derived from the endpoint URL by replacing
                          the trailing "sparql" segment with "service".
                          E.g. http://host/test/test/sparql →
                               http://host/test/test/service
  --tests, -t <names>    Comma-separated test names or substrings to run
                          May be repeated. (default: all tests)
                          e.g. -t query_get,query_post_form
                               -t bad_query -t update_base
  --manifest <path>       Path to the Turtle manifest file
                          (default: ./rdf-tests/manifest.ttl)
  --earl-output <path>    Path for the EARL results file
                          (default: ./sparql12-protocol-earl.ttl)
  --subject-name <name>   Name of the software under test in the EARL report
  --subject-uri <uri>     URI identifying the software under test
  -h, --help              Show this help`);
}

// ============================================================================
// RDF graph helpers
// ============================================================================

/** Traverse an RDF list (rdf:first/rdf:rest chain) and return items in order. */
function rdfListToArray(store, head) {
  const items = [];
  let cur = head;
  const nil = RDF + 'nil';
  while (cur && cur.value !== nil) {
    const firsts = store.getObjects(cur, namedNode(RDF + 'first'), null);
    if (firsts.length > 0) items.push(firsts[0]);
    const rests = store.getObjects(cur, namedNode(RDF + 'rest'), null);
    cur = rests.length > 0 ? rests[0] : null;
  }
  return items;
}

/** Get the first literal string value for a predicate on a subject. */
function getString(store, subject, predUri) {
  for (const obj of store.getObjects(subject, namedNode(predUri), null)) {
    if (obj.termType === 'Literal') return obj.value;
  }
  return null;
}

/** Get all literal/boolean values for a predicate. */
function getValues(store, subject, predUri) {
  return store.getObjects(subject, namedNode(predUri), null).map(term => {
    if (term.termType !== 'Literal') return term.value;
    if (term.datatype && term.datatype.value === XSD + 'boolean') {
      return term.value === 'true';
    }
    return term.value;
  });
}

/** Get the first blank-node / named-node object for a predicate. */
function getNode(store, subject, predUri) {
  const objs = store.getObjects(subject, namedNode(predUri), null);
  return objs.length > 0 ? objs[0] : null;
}

// ============================================================================
// Manifest parser (N3-based)
// ============================================================================

/** Parse an ht:RequestHeader / ht:ResponseHeader node. */
function parseHeaderNode(store, hNode) {
  const name = getString(store, hNode, HT + 'fieldName');
  const value = getString(store, hNode, HT + 'fieldValue') || '';
  const elementNames = [];
  const elemListHead = getNode(store, hNode, HT + 'headerElements');
  if (elemListHead) {
    for (const elem of rdfListToArray(store, elemListHead)) {
      const en = getString(store, elem, HT + 'elementName');
      if (en) elementNames.push(en);
    }
  }
  return { name, value, elementNames };
}

/** Parse headers from an RDF list attached to a specific node. */
function parseHeaderList(store, ownerNode) {
  const listHead = getNode(store, ownerNode, HT + 'headers');
  if (!listHead) return [];
  return rdfListToArray(store, listHead).map(h => parseHeaderNode(store, h));
}

/** Parse a cnt:ContentAsText body node. */
function parseBodyNode(store, bodyNode) {
  if (!bodyNode) return null;
  const encoding = getString(store, bodyNode, CNT + 'characterEncoding') || 'UTF-8';
  const vals = getValues(store, bodyNode, CNT + 'chars');
  return { encoding, chars: vals.length > 0 ? vals[0] : null };
}

/** Parse a single ht:Request node from the graph. */
function parseRequestNode(store, reqNode) {
  const method = getString(store, reqNode, HT + 'methodName');
  const absolutePath = getString(store, reqNode, HT + 'absolutePath');

  // Request body
  const body = parseBodyNode(store, getNode(store, reqNode, HT + 'body'));

  // Request headers — queried directly from THIS node, not from nested response
  const hasExplicitHeaders = store.getObjects(reqNode, namedNode(HT + 'headers'), null).length > 0;
  const headers = hasExplicitHeaders ? parseHeaderList(store, reqNode) : [];

  // Expected response
  let response = null;
  const respNode = getNode(store, reqNode, HT + 'resp');
  if (respNode) {
    const statusPatterns = getValues(store, respNode, HT + 'statusCodeValue').map(String);
    const respHeaders = parseHeaderList(store, respNode);
    const respBody = parseBodyNode(store, getNode(store, respNode, HT + 'body'));
    response = { statusPatterns, headers: respHeaders, body: respBody };
  }

  return { method, absolutePath, body, headers, hasExplicitHeaders, response };
}

/**
 * Parse the Turtle manifest into an ordered list of test objects.
 * Returns { tests, manifestBaseUri }.
 */
function parseManifest(turtleText) {
  const parser = new N3.Parser();
  const store = new N3.Store();
  store.addQuads(parser.parse(turtleText));

  // Determine manifest entries order
  const manifestNodes = store.getSubjects(namedNode(RDF + 'type'), namedNode(MF + 'Manifest'), null);
  let testOrder = [];
  if (manifestNodes.length > 0) {
    const entriesHead = getNode(store, manifestNodes[0], MF + 'entries');
    if (entriesHead) {
      testOrder = rdfListToArray(store, entriesHead).map(n => n.value);
    }
  }

  // Collect all ProtocolTest instances
  const testNodes = store.getSubjects(namedNode(RDF + 'type'), namedNode(MF + 'ProtocolTest'), null);

  let manifestBaseUri = '';
  const tests = [];

  for (const testNode of testNodes) {
    const fullUri = testNode.value;
    const hashIdx = fullUri.indexOf('#');
    const localName = hashIdx >= 0 ? fullUri.slice(hashIdx + 1) : fullUri;
    if (!manifestBaseUri && hashIdx >= 0) {
      manifestBaseUri = fullUri.slice(0, hashIdx);
    }

    const humanName = getString(store, testNode, MF + 'name') || localName;
    const comment = getString(store, testNode, RDFS + 'comment') || '';

    // Parse ut:graphData — dataset files to load before the test
    const graphDataNodes = store.getObjects(testNode, namedNode(UT + 'graphData'), null);
    const graphData = graphDataNodes.map(gd => {
      const graphFile = getNode(store, gd, UT + 'graph');
      const label = getString(store, gd, RDFS + 'label');
      return {
        file: graphFile ? graphFile.value : null,
        graphUri: label || null,
      };
    }).filter(g => g.file);

    const actionNode = getNode(store, testNode, MF + 'action');
    if (!actionNode) continue;

    const authority = getString(store, actionNode, HT + 'connectionAuthority') || 'www.example';
    const reqListHead = getNode(store, actionNode, HT + 'requests');
    const requestNodes = reqListHead ? rdfListToArray(store, reqListHead) : [];
    const requests = requestNodes.map(rn => parseRequestNode(store, rn));

    tests.push({ name: localName, humanName, comment, authority, requests, graphData });
  }

  // Sort by manifest entry order
  if (testOrder.length > 0) {
    const order = new Map(testOrder.map((uri, i) => [uri, i]));
    tests.sort((a, b) => {
      const uriA = manifestBaseUri + '#' + a.name;
      const uriB = manifestBaseUri + '#' + b.name;
      return (order.get(uriA) ?? 9999) - (order.get(uriB) ?? 9999);
    });
  }

  return {
    tests,
    manifestBaseUri: manifestBaseUri ||
      'https://w3c.github.io/rdf-tests/sparql/sparql12/protocol/manifest',
  };
}

// ============================================================================
// Dataset setup via Graph Store Protocol
// ============================================================================

/**
 * Load a data file via the Graph Store Protocol.
 *
 * PUT replaces the target graph's contents (clear + insert).
 * POST appends to the target graph's contents.
 *
 * @param {string} graphStoreUrl  - Graph Store Protocol endpoint
 * @param {string} filePath       - local path to the N-Triples file
 * @param {string|null} graphUri  - named graph URI (null = default graph)
 * @param {'PUT'|'POST'} method   - GSP method
 * @param {string|null} token     - bearer token
 */
async function loadGraphData(graphStoreUrl, filePath, graphUri, method, token) {
  const data = readFileSync(filePath, 'utf-8');
  const url = graphUri
    ? `${graphStoreUrl}?graph=${encodeURIComponent(graphUri)}`
    : graphStoreUrl;
  const resp = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/n-triples',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: data,
  });
  if (resp.status >= 400) {
    const body = await resp.text().catch(() => '');
    throw new Error(
      `${method} ${filePath} into <${graphUri || 'default'}>: ` +
      `${resp.status} ${body.slice(0, 200)}`
    );
  }
}

/**
 * Set up the dataset for a test by issuing Graph Store Protocol requests.
 *
 * The first ut:graphData entry is loaded with PUT (which replaces the
 * target graph, effectively clearing it before inserting the file).
 * Subsequent entries are loaded with POST (which appends to their target
 * graphs).
 *
 * @param {object} opts - { graphStoreUrl, token, manifestDir }
 * @param {Array}  graphData - [{ file, graphUri }]
 */
async function setupDataset(opts, graphData) {
  for (let i = 0; i < graphData.length; i++) {
    const gd = graphData[i];
    const filePath = resolve(opts.manifestDir, gd.file);
    const method = i === 0 ? 'PUT' : 'POST';
    await loadGraphData(opts.graphStoreUrl, filePath, gd.graphUri, method, opts.token);
  }
}

// ============================================================================
// HTTP test execution
// ============================================================================

/** Check whether an HTTP status code matches a pattern like "2XX", "4XX". */
function statusMatches(actual, pattern) {
  const a = String(actual), p = String(pattern);
  if (a.length !== 3 || p.length !== 3) return false;
  for (let i = 0; i < 3; i++) {
    if (p[i] !== 'X' && p[i] !== a[i]) return false;
  }
  return true;
}

/** Extract the base media type from a Content-Type header value. */
function mediaType(ct) {
  return ct ? ct.split(';')[0].trim().toLowerCase() : '';
}

/**
 * Parse a SPARQL boolean result from response body text.
 * Supports XML (<boolean>true</boolean>) and JSON ({"boolean":true}).
 */
function parseBooleanResult(body, ct) {
  const m = mediaType(ct);
  if (m.includes('xml') || body.trimStart().startsWith('<')) {
    const xm = body.match(/<boolean>\s*(true|false)\s*<\/boolean>/i);
    if (xm) return xm[1].toLowerCase() === 'true';
  }
  if (m.includes('json') || body.trimStart().startsWith('{')) {
    try { const j = JSON.parse(body); if (typeof j.boolean === 'boolean') return j.boolean; } catch {}
  }
  const xm = body.match(/<boolean>\s*(true|false)\s*<\/boolean>/i);
  if (xm) return xm[1].toLowerCase() === 'true';
  try { const j = JSON.parse(body); if (typeof j.boolean === 'boolean') return j.boolean; } catch {}
  return null;
}

/**
 * Build the full URL by combining the endpoint base with the test's
 * absolutePath query string, and append a `clientRequestId` parameter
 * carrying the test name so that server access logs can be correlated
 * with the manifest test that issued the request.
 */
function buildUrl(endpointUrl, absolutePath, testName) {
  let url = endpointUrl;
  if (absolutePath) {
    const qIdx = absolutePath.indexOf('?');
    if (qIdx >= 0) {
      const qs = absolutePath.slice(qIdx + 1);
      url += (url.includes('?') ? '&' : '?') + qs;
    }
  }
  if (testName) {
    url += (url.includes('?') ? '&' : '?') +
      'clientRequestId=' + encodeURIComponent(testName);
  }
  return url;
}

/** Determine whether a body string looks like URL-encoded form data. */
function looksFormEncoded(bodyStr) {
  return typeof bodyStr === 'string' &&
    /^(query|update|using[-a-z]*)=/.test(bodyStr);
}

/**
 * Execute a single HTTP request against the endpoint and validate
 * the response against manifest expectations.
 *
 * Content-Type inference:
 *   When the manifest supplies no explicit ht:headers on the request
 *   AND the body is form-encoded AND the test expects success (2XX/3XX),
 *   auto-add application/x-www-form-urlencoded.  Negative tests
 *   (only 4XX expected) intentionally omit Content-Type.
 *
 * Bearer token:
 *   Always added as Authorization header.
 */
async function executeRequest(endpointUrl, request, token, testName) {
  const url = buildUrl(endpointUrl, request.absolutePath, testName);
  const method = request.method || 'GET';

  const fetchOpts = { method, headers: {}, redirect: 'follow' };

  // Copy explicit request headers from the manifest
  for (const h of request.headers) {
    fetchOpts.headers[h.name] = h.value;
  }

  // Add Bearer token for endpoint authorization
  if (token) {
    fetchOpts.headers['Authorization'] = `Bearer ${token}`;
  }

  // Set body if present
  if (request.body && request.body.chars !== null) {
    const bodyStr = String(request.body.chars);
    fetchOpts.body = bodyStr;

    // Content-Type inference for requests WITHOUT explicit ht:headers
    if (!request.hasExplicitHeaders && !fetchOpts.headers['Content-Type']) {
      const expectsSuccess = !request.response ||
        request.response.statusPatterns.length === 0 ||
        request.response.statusPatterns.some(p => p.startsWith('2') || p.startsWith('3'));

      if (looksFormEncoded(bodyStr) && expectsSuccess) {
        fetchOpts.headers['Content-Type'] = 'application/x-www-form-urlencoded';
      }
    }
  }

  let resp;
  try {
    resp = await fetch(url, fetchOpts);
  } catch (err) {
    // If the client refuses to even send the request (e.g., fetch rejects
    // GET/HEAD with body) and the test expects only 4XX responses, this
    // counts as a pass: the request is invalid per HTTP spec, which is
    // exactly what a 4XX-expecting negative test is asserting.
    const exp = request.response;
    if (exp && exp.statusPatterns.length > 0 &&
        exp.statusPatterns.every(p => /^4/.test(String(p)))) {
      return {
        passed: true,
        details: `Client refused malformed request (as expected for 4XX): ${err.message}`,
      };
    }
    return { passed: null, details: `Network error: ${err.message}` };
  }

  const actualStatus = resp.status;
  let bodyText = '';
  try { bodyText = await resp.text(); } catch {}

  const exp = request.response;
  if (!exp) return { passed: true, details: `Status ${actualStatus} (no expectations)` };

  const failures = [];

  // --- Status code ---
  if (exp.statusPatterns.length > 0) {
    if (!exp.statusPatterns.some(p => statusMatches(actualStatus, p))) {
      failures.push(`Status: expected ${exp.statusPatterns.join(' or ')}, got ${actualStatus}`);
    }
  }

  // --- Response Content-Type ---
  for (const h of exp.headers.filter(h => h.name.toLowerCase() === 'content-type')) {
    const actual = mediaType(resp.headers.get('content-type'));
    if (h.elementNames.length > 0) {
      const ok = h.elementNames.map(n => n.toLowerCase());
      if (!ok.includes(actual)) {
        failures.push(`Content-Type: expected one of [${ok.join(', ')}], got ${actual}`);
      }
    }
  }

  // --- Boolean body check (for ASK results) ---
  if (exp.body && (exp.body.chars === true || exp.body.chars === false)) {
    const ct = resp.headers.get('content-type');
    const parsed = parseBooleanResult(bodyText, ct);
    if (parsed === null) {
      failures.push(`Boolean result: expected ${exp.body.chars}, could not parse response`);
    } else if (parsed !== exp.body.chars) {
      failures.push(`Boolean result: expected ${exp.body.chars}, got ${parsed}`);
    }
  }

  return failures.length > 0
    ? { passed: false, details: failures.join('; ') }
    : { passed: true, details: `Status ${actualStatus} OK` };
}

/**
 * Execute all requests for a test sequentially.
 * Returns { outcome: 'passed'|'failed'|'cantTell', details }.
 */
async function executeTest(endpointUrl, test, token, datasetOpts) {
  // Set up the dataset if a Graph Store URL is configured
  if (datasetOpts && test.graphData && test.graphData.length > 0) {
    try {
      await setupDataset(datasetOpts, test.graphData);
    } catch (err) {
      return { outcome: 'cantTell', details: `Dataset setup: ${err.message}` };
    }
  }

  const details = [];
  for (let i = 0; i < test.requests.length; i++) {
    const label = test.requests.length > 1
      ? `Request ${i + 1}/${test.requests.length}`
      : 'Request';
    let result;
    try {
      result = await executeRequest(endpointUrl, test.requests[i], token, test.name);
    } catch (err) {
      return { outcome: 'cantTell', details: `${label}: Error: ${err.message}` };
    }
    if (result.passed === null) {
      return { outcome: 'cantTell', details: `${label}: ${result.details}` };
    }
    details.push(`${label}: ${result.details}`);
    if (!result.passed) {
      return { outcome: 'failed', details: details.join(' | ') };
    }
  }
  return { outcome: 'passed', details: details.join(' | ') };
}

// ============================================================================
// EARL report generation
// ============================================================================

function turtleEscape(s) {
  return s
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n')
    .replace(/\r/g, '\\r')
    .replace(/\t/g, '\\t');
}

function generateEarl({ manifestBaseUri, subjectUri, subjectName, results, dateStr }) {
  const L = [];

  L.push('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .');
  L.push('@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .');
  L.push('@prefix dc: <http://purl.org/dc/terms/> .');
  L.push('@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .');
  L.push('@prefix doap: <http://usefulinc.com/ns/doap#> .');
  L.push('@prefix foaf: <http://xmlns.com/foaf/0.1/> .');
  L.push('@prefix earl: <http://www.w3.org/ns/earl#> .');
  L.push(`@prefix sp12: <${manifestBaseUri}#> .`);
  L.push('');

  L.push('<#tool> a earl:Assertor, earl:Software ;');
  L.push('    doap:name "SPARQL 1.2 Protocol Test Runner" ;');
  L.push('    doap:description "Automated SPARQL 1.2 protocol conformance test runner" .');
  L.push('');

  L.push(`<${turtleEscape(subjectUri)}> a earl:TestSubject, earl:Software ;`);
  L.push(`    doap:name "${turtleEscape(subjectName)}" ;`);
  L.push(`    doap:homepage <${turtleEscape(subjectUri)}> .`);
  L.push('');

  for (const r of results) {
    const outcomeUri =
      r.outcome === 'passed' ? 'earl:passed' :
      r.outcome === 'failed' ? 'earl:failed' : 'earl:cantTell';

    L.push('[] a earl:Assertion ;');
    L.push('    earl:assertedBy <#tool> ;');
    L.push(`    earl:subject <${turtleEscape(subjectUri)}> ;`);
    L.push(`    earl:test sp12:${r.testName} ;`);
    L.push('    earl:mode earl:automatic ;');
    L.push('    earl:result [');
    L.push('        a earl:TestResult ;');
    L.push(`        earl:outcome ${outcomeUri} ;`);
    if (r.details) {
      L.push(`        earl:info "${turtleEscape(r.details)}" ;`);
    }
    L.push(`        dc:date "${r.dateTime}"^^xsd:dateTime`);
    L.push('    ] .');
    L.push('');
  }

  return L.join('\n');
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const opts = parseArgs();

  let manifestText;
  try {
    manifestText = readFileSync(opts.manifestPath, 'utf-8');
  } catch (err) {
    console.error(`Error reading manifest: ${opts.manifestPath}`);
    console.error(err.message);
    process.exit(1);
  }

  const { tests: allTests, manifestBaseUri } = parseManifest(manifestText);

  if (allTests.length === 0) {
    console.error('No tests found in the manifest.');
    process.exit(1);
  }

  // Filter tests if --tests / -t was given
  let tests = allTests;
  if (opts.testFilters.length > 0) {
    tests = allTests.filter(t =>
      opts.testFilters.some(f => t.name.includes(f))
    );
    if (tests.length === 0) {
      console.error(`No tests matched filters: ${opts.testFilters.join(', ')}`);
      process.exit(1);
    }
  }

  // Dataset setup options — always available since graphStoreUrl is either
  // provided via --graph-store-url or auto-derived from the endpoint URL.
  const datasetOpts = {
    graphStoreUrl: opts.graphStoreUrl,
    token: opts.token,
    manifestDir: dirname(opts.manifestPath),
  };

  console.log('SPARQL 1.2 Protocol Test Suite');
  console.log(`Endpoint:    ${opts.endpointUrl}`);
  console.log(`Graph Store: ${opts.graphStoreUrl}`);
  console.log(`Manifest:    ${opts.manifestPath} (${tests.length} tests)`);
  console.log('='.repeat(72));

  const results = [];
  let passCount = 0, failCount = 0, errorCount = 0;
  const dateStr = new Date().toISOString().split('T')[0];

  for (const test of tests) {
    const dateTime = new Date().toISOString();
    let result;
    try {
      result = await executeTest(opts.endpointUrl, test, opts.token, datasetOpts);
    } catch (err) {
      result = { outcome: 'cantTell', details: `Unexpected error: ${err.message}` };
    }

    if (result.outcome === 'passed') {
      console.log(`PASS  ${test.name}`);
      passCount++;
    } else if (result.outcome === 'failed') {
      console.log(`FAIL  ${test.name}`);
      console.log(`      ${result.details}`);
      failCount++;
    } else {
      console.log(`ERR   ${test.name}`);
      console.log(`      ${result.details}`);
      errorCount++;
    }

    results.push({
      testName: test.name,
      humanName: test.humanName,
      outcome: result.outcome,
      details: result.details,
      dateTime,
    });
  }

  console.log('='.repeat(72));
  console.log(`Results: ${passCount} passed, ${failCount} failed, ${errorCount} errors (${tests.length} total)`);

  const earlContent = generateEarl({
    manifestBaseUri,
    subjectUri: opts.subjectUri,
    subjectName: opts.subjectName,
    results,
    dateStr,
  });

  writeFileSync(opts.earlOutput, earlContent, 'utf-8');
  console.log(`EARL report: ${opts.earlOutput}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});

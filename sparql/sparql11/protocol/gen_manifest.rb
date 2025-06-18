require 'cgi'
require 'getoptlong'
require 'json/ld'
require 'rdf/rdfa'
require 'rdf/reasoner'
require 'rdf/turtle'
require 'haml'
require 'htmlbeautifier'

# Test descriptions used for generating Manifest and HTML renderings.
#
# ### Request (`req`):
# * `method`: HTTP request method
# * `content`: HTTP request content. If an object/hash, used to create application/x-www-form-urlencoded content. If the request `Content-Type` header indicates a text encoding this MUST be used for encoding any POST content.
# * `Accept`: HTTP request accept header
# * `Content-Type`: HTTP request content-type (defaults to `application/x-www-form-urlencoded` for POST).
# * Other entries are encoded as request query parameters.
#
# If `req` has more than one entry, the intermediate response is expected to be a success with the following `resp` description used to match the final response.
#
# ### Response (`resp`):
# `status`: HTTP response status to match.
# `Content-Type`: response content-type expected to match one of these.
POSITIVE_TESTS = {
  query_get: {
    name: "query via GET",
    req: [{
      method: :GET,
      query: "ASK {}",
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_post_form: {
    name: "query via URL-encoded POST",
    req: [{
      method: :POST,
      query: "ASK {}",
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_post_direct: {
    name: "query via POST directly",
    req: [{
      method: :POST,
      content: "ASK {}",
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      "Content-Type": "application/sparql-query",
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_default_graph: {
    name: "query with protocol-specified default graph",
    req: [{
      method: :POST,
      content: {
        query: 'ASK { <http://kasei.us/2009/09/sparql/data/data1.rdf> ?p ?o }',
        "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data1.rdf",
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_default_graphs_get: {
    name: "GET query with protocol-specified default graphs",
    req: [{
      method: :GET,
      query: 'ASK { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type . <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type . }',
      "default-graph-uri": %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_default_graphs_post: {
    name: "POST query with protocol-specified default graphs",
    req: [{
      method: :POST,
      content: {
        query: 'ASK { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type . <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type . }',
        "default-graph-uri": %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_named_graphs_post: {
    name: "POST query with protocol-specified named graphs",
    req: [{
      method: :POST,
      content: {
        query: 'ASK { GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type } GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type } }',
        "named-graph-uri": %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_named_graphs_get: {
    name: "GET query with protocol-specified named graphs",
    req: [{
      method: :GET,
      query: 'ASK { GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type } GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type } }',
      "named-graph-uri": %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_dataset_full: {
    name: "query with protocol-specified dataset (both named and default graphs)",
    req: [{
      method: :POST,
      content: {
        query: %(
ASK {
  <http://kasei.us/2009/09/sparql/data/data3.rdf> a ?type
  GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type }
  GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type }
}
),
        'default-graph-uri': 'http://kasei.us/2009/09/sparql/data/data3.rdf',
        'named-graph-uri': %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_multiple_dataset: {
    name: "query specifying dataset in both query string and protocol; test for use of protocol-specified dataset",   
    req: [{
      method: :POST,
      content: {
        query: 'ASK FROM <http://kasei.us/2009/09/sparql/data/data3.rdf> { GRAPH ?g1 { <http://kasei.us/2009/09/sparql/data/data1.rdf> a ?type } GRAPH ?g2 { <http://kasei.us/2009/09/sparql/data/data2.rdf> a ?type } }',
        'named-graph-uri': %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json),
        content: true
      }
    }],
  },
  query_content_type_select: {
    name: "SELECT query appropriate content type (expect one of: XML, JSON, CSV, TSV)",
    req: [{
      method: :POST,
      content: {
        query: 'SELECT (1 AS ?value) {}',
        'default-graph-uri': 'http://kasei.us/2009/09/sparql/data/data0.rdf',
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json text/tab-separated-values text/csv)
      }
    }],
  },
  query_content_type_ask: {
    name: "ASK query appropriate content type (expect one of: XML, JSON)",
    req: [{
      method: :POST,
      content: {
        query: 'ASK {}',
        'default-graph-uri': 'http://kasei.us/2009/09/sparql/data/data0.rdf',
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/sparql-results+xml application/sparql-results+json)
      }
    }],
  },
  query_content_type_describe: {
    name: "DESCRIBE query appropriate content type (expect one of: RDF/XML, Turtle, N-Triples, RDFa, JSON-LD)",
    req: [{
      method: :POST,
      content: {
        query: 'DESCRIBE <http://example.org/>',
        'default-graph-uri': 'http://kasei.us/2009/09/sparql/data/data0.rdf',
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/rdf+xml text/turtle application/n-triples text/html application/ld+json)
      }
    }],
  },
  query_content_type_construct: {
    name: "CONSTRUCT query appropriate content type (expect one of: RDF/XML, Turtle, N-Triples, RDFa, JSON-LD))",
    req: [{
      method: :POST,
      content: {
        query: 'CONSTRUCT { <s> <p> 1 } WHERE {}',
        'default-graph-uri': 'http://kasei.us/2009/09/sparql/data/data0.rdf',
      },
      resp: {
        status: %w(2XX 3XX),
        "Content-Type": %w(application/rdf+xml text/turtle application/n-triples text/html application/ld+json)
      }
    }],
  },
  update_dataset_default_graph: {
    name: "update with protocol-specified default graph",
    req: [{
      method: :POST,
      content: {
        update: %(
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
CLEAR ALL ;
INSERT DATA {
  GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> {
    <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document
  }
} ;
INSERT {
  GRAPH <http://example.org/protocol-update-dataset-test/> {
    ?s a dc:BibliographicResource
  }
}
WHERE {
  ?s a foaf:Document
}
)
},
      'using-graph-uri': 'http://kasei.us/2009/09/sparql/data/data1.rdf',
      resp: {
        status: %w(2XX 3XX)
      }
    }, {
      method: :POST,
      content: %(
ASK {
  GRAPH <http://example.org/protocol-update-dataset-test/> {
    <http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource>
  }
}
),
      'Content-Type': 'application/sparql-query',
      'Accept': 'application/sparql-results+xml',
      resp: {
        status: %w(2XX 3XX),
        'Content-Type': 'application/sparql-results+xml'
      }
    }],
  },
  update_dataset_default_graphs: {
    name: "update with protocol-specified default graphs",
    req: [{
      method: :POST,
      content: {
      update: %(
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
  GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
  GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
    ?s a dc:BibliographicResource
  }
}
WHERE {
  ?s a foaf:Document
}
)
},
      'using-graph-uri': %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      resp: {
        status: %w(2XX 3XX)
      }
    }, {
      method: :POST,
      content: %(
ASK {
  GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
    <http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
    <http://kasei.us/2009/09/sparql/data/data2.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
  }
  FILTER NOT EXISTS {
    GRAPH <http://example.org/protocol-update-dataset-graphs-test/> {
      <http://kasei.us/2009/09/sparql/data/data3.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
    }
  }
}
),
      'Content-Type': 'application/sparql-query',
      'Accept': 'application/sparql-results+xml',
      resp: {
        status: %w(2XX 3XX),
        'Content-Type': 'application/sparql-results+xml'
      }
    }],
  },
  update_dataset_named_graphs: {
    name: "update with protocol-specified named graphs",
    req: [{
      method: :POST,
      content: {
      update: %(
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
  GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
  GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
    ?s a dc:BibliographicResource
  }
}
WHERE {
  GRAPH ?g {
    ?s a foaf:Document
  }
}
)
},
      'using-graph-uri': %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      resp: {
        status: %w(2XX 3XX)
      }
    }, {
      method: :POST,
      content: %(
ASK {
  GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
    <http://kasei.us/2009/09/sparql/data/data1.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
    <http://kasei.us/2009/09/sparql/data/data2.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
  }
  FILTER NOT EXISTS {
    GRAPH <http://example.org/protocol-update-dataset-named-graphs-test/> {
      <http://kasei.us/2009/09/sparql/data/data3.rdf> a <http://purl.org/dc/terms/BibliographicResource> .
    }
  }
}
),
      'Content-Type': 'application/sparql-query',
      'Accept': 'application/sparql-results+xml',
      resp: {
        status: %w(2XX 3XX),
        'Content-Type': 'application/sparql-results+xml'
      }
    }],
  },
  update_dataset_full: {
    name: "update with protocol-specified dataset (both named and default graphs)",
    req: [{
      method: :POST,
      update: %(
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
DROP ALL ;
INSERT DATA {
  GRAPH <http://kasei.us/2009/09/sparql/data/data1.rdf> { <http://kasei.us/2009/09/sparql/data/data1.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data2.rdf> { <http://kasei.us/2009/09/sparql/data/data2.rdf> a foaf:Document }
  GRAPH <http://kasei.us/2009/09/sparql/data/data3.rdf> { <http://kasei.us/2009/09/sparql/data/data3.rdf> a foaf:Document }
} ;
INSERT {
  GRAPH <http://example.org/protocol-update-dataset-full-test/> {
    ?s <http://example.org/in> ?in
  }
}
WHERE {
  {
    GRAPH ?g { ?s a foaf:Document }
    BIND(?g AS ?in)
  }
  UNION
  {
    ?s a foaf:Document .
    BIND("default" AS ?in)
  }
}
),
      'using-graph-uri': %w(http://kasei.us/2009/09/sparql/data/data1.rdf http://kasei.us/2009/09/sparql/data/data2.rdf),
      resp: {
        status: %w(2XX 3XX)
      }
    }, {
      method: :POST,
      content: %(
ASK {
  GRAPH <http://example.org/protocol-update-dataset-full-test/> {
    <http://kasei.us/2009/09/sparql/data/data1.rdf> <http://example.org/in> "default" .
    <http://kasei.us/2009/09/sparql/data/data2.rdf> <http://example.org/in> <http://kasei.us/2009/09/sparql/data/data2.rdf> .
  }
  FILTER NOT EXISTS {
    GRAPH <http://example.org/protocol-update-dataset-full-test/> {
      <http://kasei.us/2009/09/sparql/data/data3.rdf> ?p ?o
    }
  }
}
),
      'Content-Type': 'application/sparql-query',
      'Accept': 'application/sparql-results+xml',
      resp: {
        status: %w(2XX 3XX),
        'Content-Type': 'application/sparql-results+xml'
      }
    }],
  },
  update_post_form: {
    name: "update via URL-encoded POST",
    req: [{
      method: :POST,
      content: {
        update: 'CLEAR ALL'
      },
      resp: {
        status: %w(2XX 3XX)
      }
    }]
  },
  update_post_direct: {
    name: "update via POST directly",
    req: [{
      method: :POST,
      content: 'CLEAR ALL',
      'Content-Type': 'application/sparql-update',
      resp: {
        status: %w(2XX 3XX)
      }
    }]
  },
  update_base_uri: {
    name: "test for service-defined BASE URI (\"which MAY be the service endpoint\")",
    req: [{
      method: :POST,
      content: {
        update: 'CLEAR SILENT GRAPH <http://example.org/protocol-base-test/> ; INSERT DATA { GRAPH <http://example.org/protocol-base-test/> { <http://example.org/s> <http://example.org/p> <test> } }'
      },
      resp: {
        status: %w(2XX 3XX)
      }
    }, {
      method: :POST,
      content: {
        query: 'SELECT ?o WHERE { GRAPH <http://example.org/protocol-base-test/> { <http://example.org/s> <http://example.org/p> ?o } }'
      },
      'Accept': 'application/sparql-results+xml',
      resp: {
        status: %w(2XX 3XX),
        'Content-Type': 'application/sparql-results+xml',
        content: "one result with `?o` bound to an IRI that is _not_ `<test>`"
      }
    }]
  },
}

NEGATIVE_TESTS  = {
  bad_query_method: {
    name: "invoke query operation with a method other than GET or POST",
    req: [{
      method: :PUT,
      query: "ASK {}",
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_multiple_queries: {
    name: "invoke query operation with more than one query string",
    req: [{
      method: :GET,
      query: ["ASK {}", "SELECT * {}"],
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_query_wrong_media_type: {
    name: "invoke query operation with a POST with media type that's not url-encoded or application/sparql-query",
    req: [{
      method: :POST,
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      'Content-Type': 'text/plain',
      content: 'ASK {}',
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_query_missing_form_type: {
    name: "invoke query operation with url-encoded body, but without application/x-www-form-urlencoded media type",
    req: [{
      method: :POST,
      content: {
        query: "ASK {}",
        "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf"
      },
      'Content-Type': nil,
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_query_missing_direct_type: {
    name: "invoke query operation with SPARQL body, but without application/sparql-query media type",
    req: [{
      method: :POST,
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      content: "ASK {}",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_query_non_utf8: {
    name: "invoke query operation with direct POST, but with a non-UTF8 encoding (UTF-16)",
    req: [{
      method: :POST,
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      'Content-Type': 'application/sparql-query; charset=UTF-16',
      content: 'ASK {}',
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_query_syntax: {
    name: "invoke query operation with invalid query syntax (4XX result)",
    req: [{
      method: :GET,
      query: 'ASK {',
      "default-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_get: {
    name: "invoke update operation with GET",
    req: [{
      method: :GET,
      update: 'CLEAR ALL',
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_multiple_updates: {
    name: "invoke update operation with more than one update string",
    req: [{
      method: :POST,
      content: {
        update: ['CLEAR ALL', 'CLEAR DEFAULT']
      },
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_wrong_media_type: {
    name: "invoke update operation with a POST with media type that's not url-encoded or application/sparql-update",
    req: [{
      method: :POST,
      content: 'CLEAR NAMED',
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      'Content-Type': 'text/plain',
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_missing_form_type: {
    name: "invoke update operation with url-encoded body, but without application/x-www-form-urlencoded media type",
    req: [{
      method: :POST,
      content: 'CLEAR NAMED',
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      'Content-Type': nil,
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_non_utf8: {
    name: "invoke update operation with direct POST, but with a non-UTF8 encoding",
    req: [{
      method: :POST,
      content: 'CLEAR NAMED',
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      'Content-Type': 'application/sparql-update; charset=UTF-16',
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_syntax: {
    name: "invoke update operation with invalid update syntax (4XX result)",
    req: [{
      method: :POST,
      content: {
        update: 'CLEAR XYZ'
      },
      "using-graph-uri": "http://kasei.us/2009/09/sparql/data/data0.rdf",
      resp: {
        status: "4XX"
      }
    }],
  },
  bad_update_dataset_conflict: {
    name: "invoke update with both using-graph-uri/using-named-graph-uri parameter and USING/WITH clause",
    req: [{
      method: :POST,
      content: {
        "using-named-graph-uri": "http://example/people",
        update: %(
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
WITH <http://example/addresses>
DELETE { ?person foaf:givenName 'Bill' }
INSERT { ?person foaf:givenName 'William' }
WHERE {
  ?person foaf:givenName 'Bill'
}
),
      },
      "Content-Type": "application/x-www-form-urlencoded",
      resp: {
        status: "4XX"
      }
    }],
  },
}

def req_uri(params)
  params.map do |key, values|
    unless %i(method name content resp Content-Type Accept).include?(key)
      Array(values).map do |value|
        "#{key}=#{CGI.escape(value.to_s).gsub('+', '%20')}"
      end.join('&')
    end
  end.compact.join('&')
end

def encode_header(params, field)
  values = Array(params[field]).map(&:to_s)
  h_field = {
      "@type": "ht:RequestHeader",
      "ht:fieldName": field,
      "ht:fieldValue": Array(values).join(', ')
    }

  values.each do |value|
    value, *params = value.split(';').map(&:strip)
    element = {
      "@type": "ht:HeaderElement",
      "ht:elementName": value
    }
    params.each do |param|
      p, v = param.split('=')
      pv = v.sub(/^["']?([^"']*)["']?$/, '\1')
      # Remember charset for body encoding
      $charset = pv if p.downcase == 'charset'
      param = {
        "@type": "ht:Parameter",
        "ht:paramName": p,
        "ht:paramValue": pv
      }

      (element[:params] ||= []) << param
    end

    (h_field[:headerElements] ||= []) << element
  end

  h_field
end

def encode_body(content)
  content = req_uri(content) if content.is_a?(Hash)
  {
    "@type": "cnt:ContentAsText",
    "cnt:chars": content,
    "cnt:characterEncoding": $charset
  }
end

def gen_entry(frag, params)
  $charset = "UTF-8"
  entry = {
    '@id': "##{frag}",
    "@type": "mf:ProtocolTest",
    "name": params.delete(:name),
    "approval": "dawgt:Approved",
    "approvedBy": "http://www.w3.org/2009/sparql/meeting/2012-11-20#resolution_3",
    "action": {
      "@type": "ht:Connection",
      "ht:connectionAuthority": "www.example",
      "requests": []
    }
  }
  requests = entry[:action][:requests]
  params[:req].each do |req|
    uri_query = req_uri(req)
    path = uri_query.to_s.empty? ? "/sparql" : "/sparql?#{uri_query}"
    request = {
      "@type": "ht:Request",
      "ht:methodName": req[:method],
      "ht:httpVersion": "1.1",
      "ht:absolutePath": path,
    }

    # Headers
    (request[:headers] ||= []) << encode_header(req, :Accept) if
      req[:Accept]

    # Default Content-Type on POST
    #req[:'Content-Type'] = "application/x-www-form-urlencoded" if
    #  req[:method] == :POST && !req.key?(:'Content-Type')

    (request[:headers] ||= []) << encode_header(req, :'Content-Type') if
      req[:'Content-Type']

    request[:"ht:body"] = encode_body(req[:content]) if req[:content]

    if resp = req.delete(:resp)
      response = {
        "@type": "ht:Response",
        "ht:statusCodeValue": Array(resp[:status])
      }

      (response[:headers] ||= []) << encode_header(resp, :'Content-Type') if
        resp[:'Content-Type']

      response[:"ht:body"] = encode_body(resp[:content]) if resp[:content]

      request[:"ht:resp"] = response
    end

    requests << request
  end
  entry
end

def validate(reader)
  RDF::Reasoner.apply(:rdfs, :owl)
  graph = RDF::Graph.new {|g| g << reader}
  graph.entail!
  messages = graph.lint
  messages.each do |kind, term_messages|
    term_messages.each do |term, messages|
      STDERR.puts "#{kind}  #{term}"
      messages.each {|m| options[:output].puts "  #{m}"}
    end
  end
  exit 1 unless messages.empty?
end

# Generate JSON-LD describing the test manifest
man = {
  "@context": {
    "@base":  "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest",
    "cnt":    "http://www.w3.org/2011/content#",
    "dawgt":  "http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#",
    "ht":     "http://www.w3.org/2011/http#",
    "mf":     "http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#",
    "mq":     "http://www.w3.org/2001/sw/DataAccess/tests/test-query#",
    "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",

    "action":               {"@id": "mf:action", "@type": "@id"},
    "approval":             {"@id": "dawgt:approval", "@type": "@id"},
    "approvedBy":           {"@id": "dawgt:approvedBy", "@type": "@id"},
    "comment":              {"@id": "rdfs:comment"},
    "data":                 {"@id": "mq:data", "@type": "@id"},
    "entries":              {"@id": "mf:entries", "@container": "@list", "@type": "@id"},
    "feature":              {"@id": "mf:feature", "@type": "@vocab"},
    "graphData":            {"@id": "mq:graphData", "@type": "@id"},
    "label":                {"@id": "rdfs:label"},
    "name":                 {"@id": "mf:name"},
    "notable":              {"@id": "mf:notable", "@type": "@vocab"},
    "query":                {"@id": "mq:query", "@type": "@id"},
    "queryForm":            {"@id": "mq:queryForm", "@type": "@vocab"},
    "requires":             {"@id": "mf:requires", "@type": "@vocab", "@container": "@set"},
    "result":               {"@id": "mf:result", "@type": "@id"},

    "headerElements":       {"@id": "ht:headerElements", "@container": "@list"},
    "headers":              {"@id": "ht:headers", "@container": "@list"},
    "params":               {"@id": "ht:params", "@container": "@list"},
    "requests":             {"@id": "ht:requests", "@container": "@list"},
  },
  "@id": "",
  "@type": "mf:Manifest",
  "label": "SPARQL Protocol",
  "comment": %(
Test descriptions used for generating Manifest and HTML renderings.
Test HTTP connection described using HTTP and CNT vocabularies.
In responses, status values such as "2XX", "3XX" are used to match the actual response status.
Multiple values for Content-Type mean that the response MUST include one or more of these types.
Responses for ASK match any specified boolean content.
Some tests require special result processing.
  ),
  "entries": []
}

POSITIVE_TESTS.merge(NEGATIVE_TESTS).each do |frag, params|
  entry = gen_entry(frag, params)
  man[:entries] << entry
end

OPT_ARGS = [
  ["--help", "-?",      GetoptLong::NO_ARGUMENT, "print this message"],
  ["--format", "-f",    GetoptLong::REQUIRED_ARGUMENT, "Output format (jsonld, ttl or html)"],
  ["--output", "-o",    GetoptLong::REQUIRED_ARGUMENT, "Output to specified file"],
  ["--validate",        GetoptLong::NO_ARGUMENT, "Validate the resulting graph"],
]

def usage(**options)
  STDERR.puts %{
    generate protocol manifests
    
    Usage: #{$0} [options]
  }.gsub(/^    /, '')
  width = OPT_ARGS.map do |o|
    l = o.first.length
    l += o[1].length + 2 if o[1].is_a?(String)
    l
  end.max
  OPT_ARGS.each do |o|
    s = "  %-*s  " % [width, (o[1].is_a?(String) ? "#{o[0,2].join(', ')}" : o[0])]
    s += o.last
    STDERR.puts s
  end
  exit(1)
end

opts = GetoptLong.new(*OPT_ARGS.map {|o| o[0..-2]})

format = :jsonld
output = $stdout
validate = false

opts.each do |opt, arg|
  case opt
  when '--help'         then usage
  when '--format'       then format = arg.to_sym
  when '--output'       then output = File.open(arg, "w")
  when '--validate'     then validate = true
  end
end

case format
when :html
  template = File.read(File.expand_path('../template.haml', __FILE__))
  haml_runner = if Haml::VERSION >= "6"
    Haml::Template.new(format: :html5) {template}
  else
    Haml::Engine.new(template, format: :html5)
  end
  html = haml_runner.render(self, man: JSON.parse(man.to_json))
  validate(RDF::RDFa::Reader.new(html, base_uri: "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest.ttl", validate: validate)) if validate
  beautified = HtmlBeautifier.beautify(html) + "\n"
  output.write(html)
when :jsonld
  validate(JSON::LD::Reader.new(man.to_json, base_uri: "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest.ttl", validate: validate)) if validate
  output.puts man.to_json(JSON::LD::JSON_STATE)
when :ttl
  JSON::LD::Reader.new(man.to_json, validate: validate) do |reader|
    ttl = RDF::Turtle::Writer.buffer(
      prefixes: {
        "":     "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest#",
        cnt:    "http://www.w3.org/2011/content#",
        dawgt:  "http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#",
        ht:     "http://www.w3.org/2011/http#",
        mf:     "http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#",
        qt:     "http://www.w3.org/2001/sw/DataAccess/tests/test-query#",
        rdf:    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        rdfs:   "http://www.w3.org/2000/01/rdf-schema#",
      }
    ) {|writer| writer << reader}

    validate(RDF::Turtle::Reader.new(ttl, base_uri: "http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest.ttl", validate: true)) if validate

    # Do some result hacking
    ttl.sub!('<http://www.w3.org/2009/sparql/docs/tests/data-sparql11/protocol/manifest>', '<>')
    ttl.sub!(/mf:entries \((.*)\) \.$/) do |matched|
      matched.sub('(:', '( :').gsub(' :', "\n    :")
    end
    
    output.write(ttl)
  end
else
  STDERR.puts "unknown output format #{format}"
  usage
end


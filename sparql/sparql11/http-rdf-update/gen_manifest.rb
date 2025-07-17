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
  put__initial_state: {
    name: "PUT - Initial state",
    req: [{
      method: :PUT,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:fn "John Doe"
    ].
),
      resp: {
        status: %w(201)
      }
    }],
  },
  get_of_put__initial_state: {
    name: "GET of PUT - Initial state",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$?graph=$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
   foaf:businessCard [
        a v:VCard;
        v:fn "John Doe"
   ].
)
      }
    }],
  },
  put__graph_already_in_store: {
    name: "PUT - graph already in store",
    req: [{
      method: :PUT,
      path: "$GRAPHSTORE$/person/1",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:fn "Jane Doe"
    ].
),
      resp: {
        status: %w(204),
      }
    }],
  },
  get_of_put__graph_already_in_store: {
    name: "GET of PUT - graph already in store",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$/person/1",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
   foaf:businessCard [
        a v:VCard;
        v:fn "Jane Doe"
   ] .
)
      }
    }],
  },
  put__default_graph: {
    name: "PUT - default graph",
    req: [{
      method: :PUT,
      path: "$GRAPHSTORE$?default",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

[]  a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:given-name "Alice"
    ] .
),
      resp: {
        status: %w(201),
      }
    }],
  },
  get_of_put__default_graph: {
    name: "GET of PUT - default graph",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$?default",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

[]  a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:given-name "Alice"
    ] .
)
      }
    }],
  },
  put__mismatched_payload: {
    name: "PUT - mismatched payload",
    req: [{
      method: :PUT,
      path: "$GRAPHSTORE$?default",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:fn "Jane Doe"
    ].
),
      resp: {
        status: %w(400),
      }
    }],
  },
  delete__existing_graph: {
    name: "DELETE - existing graph",
    req: [{
      method: :DELETE,
      path: "$GRAPHSTORE$/person/2.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(200),
      }
    }],
  },
  get_of_delete__existing_graph: {
    name: "GET of DELETE - existing graph",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$/person/2.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(404),
      }
    }],
  },
  delete__nonexistent_graph: {
    name: "DELETE - non-existent graph)",
    req: [{
      method: :DELETE,
      path: "$GRAPHSTORE$/person/2.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(404),
      }
    }],
  },
  post__existing_graph: {
    name: "POST - existing graph",   
    req: [{
      method: :POST,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

<http://$HOST$/$GRAPHSTORE$/person/1> foaf:name "Jane Doe"
),
      resp: {
        status: %w(200),
      }
    }],
  },
  get_of_post__existing_graph: {
    name: "GET of POST - existing graph",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
    foaf:name "Jane Doe";
    foaf:businessCard [ 
        a v:VCard;
        v:fn "Jane Doe" 
    ] .            
)
      }
    }],
  },
  post__multipart_formdata: {
    name: "POST - multipart/form-data",
    req: [{
      method: :POST,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      "Content-Type": "multipart/form-data; boundary=a6fe4cd636164618814be9f8d3d1a0de",
      content: %(
--a6fe4cd636164618814be9f8d3d1a0de
Content-Disposition: form-data; name="lastName.ttl"; filename="lastName.ttl"
Content-Type: text/turtle; charset=utf-8

@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<http://$HOST$/$GRAPHSTORE$/person/1> foaf:familyName "Doe"

--a6fe4cd636164618814be9f8d3d1a0de
Content-Disposition: form-data; name="firstName.ttl"; filename="firstName.ttl"
Content-Type: text/turtle; charset=utf-8

@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<http://$HOST$/$GRAPHSTORE$/person/1> foaf:givenName "Jane"

--a6fe4cd636164618814be9f8d3d1a0de--
      ),
      resp: {
        status: %w(200),
      }
    }],
  },
  get_of_post__multipart_formdata: {
    name: "GET of POST - multipart/form-data",
    req: [{
      method: :GET,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

<http://$HOST$/$GRAPHSTORE$/person/1> a foaf:Person;
    foaf:name           "Jane Doe";
    foaf:givenName      "Jane";
    foaf:familyName     "Doe";
    foaf:businessCard [
        a               v:VCard;
        v:fn            "Jane Doe"
    ] .
)
      }
    }],
  },
  post__create__new_graph: {
    name: "POST - create new graph",
    req: [{
      method: :POST,
      path: "$GRAPHSTORE$",
      Host: "$HOST$",
      "Content-Type": "text/turtle; charset=utf-8",
      content: %(
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix v: <http://www.w3.org/2006/vcard/ns#> .

[]  a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:given-name "Alice"
    ] .
),
      resp: {
        status: %w(201),
        Location: "$NEWPATH$"
      }
    }],
  },
  get_of_post__create__new_graph: {
    name: "GET of POST - create new graph",
    req: [{
      method: :GET,
      path: "$NEWPATH$",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
[]  a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:given-name "Alice"
    ] .
)
      }
    }],
  },
  get_of_post__after_noop: {
    name: "GET of POST - after noop",
    req: [{
      method: :GET,
      path: "$NEWPATH$",
      Host: "$HOST$",
      Accept: "text/turtle",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
        content: %(
[]  a foaf:Person;
    foaf:businessCard [
        a v:VCard;
        v:given-name "Alice"
    ] .
)
      }
    }]
  },
  head_on_an_existing_graph: {
    name: "",
    req: [{
      method: :HEAD,
      path: "$GRAPHSTORE$/person/1.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(200),
        "Content-Type": "text/turtle; charset=utf-8",
      }
    }]
  },
  head_on_a_nonexisting_graph: {
    name: "HEAD on a non-existing graph",
    req: [{
      method: :HEAD,
      path: "$GRAPHSTORE$/person/4.ttl",
      Host: "$HOST$",
      resp: {
        status: %w(404),
      }
    }]
  }
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
    "@type": "mf:GraphStoreProtocolTest",
    "name": params.delete(:name),
    "approval": "dawg:Approved",
    "approvedBy": "http://www.w3.org/2009/sparql/meeting/2012-11-20#resolution_3",
    "action": {
      "@type": "ht:Connection",
      "ht:connectionAuthority": "www.example",
      "requests": []
    }
  }
  requests = entry[:action][:requests]
  params[:req].each do |req|
    path = req[:path]
    request = {
      "@type": "ht:Request",
      "ht:methodName": req[:method],
      "ht:httpVersion": "1.1",
      "ht:absolutePath": path,
    }

    # Headers
    req.each_key do |key|
      next unless key.to_s.start_with?(/[A-Z]/)
      (request[:headers] ||= []) << encode_header(req, key)
    end

    request[:"ht:body"] = encode_body(req[:content]) if req[:content]

    if resp = req.delete(:resp)
      response = {
        "@type": "ht:Response",
        "ht:statusCodeValue": Array(resp[:status])
      }

      resp.each_key do |key|
        next unless key.to_s.start_with?(/[A-Z]/)
        (request[:headers] ||= []) << encode_header(resp, key)
      end

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
    "@base":  "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/manifest",
    "cnt":    "http://www.w3.org/2011/content#",
    "dawg":   "http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#",
    "ht":     "http://www.w3.org/2011/http#",
    "mf":     "http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#",
    "mq":     "http://www.w3.org/2001/sw/DataAccess/tests/test-query#",
    "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",

    "action":               {"@id": "mf:action", "@type": "@id"},
    "approval":             {"@id": "dawg:approval", "@type": "@id"},
    "approvedBy":           {"@id": "dawg:approvedBy", "@type": "@id"},
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
  "label": "SPARQL Graph Store Protocol",
  "entries": []
}

POSITIVE_TESTS.each do |frag, params|
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
    generate Graph Store Protocol manifests
    
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
  validate(RDF::RDFa::Reader.new(html, base_uri: "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/manifest", validate: validate)) if validate
  beautified = HtmlBeautifier.beautify(html) + "\n"
  output.write(beautified)
when :jsonld
  validate(JSON::LD::Reader.new(man.to_json, base_uri: "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/manifest", validate: validate)) if validate
  output.puts man.to_json(JSON::LD::JSON_STATE)
when :ttl
  JSON::LD::Reader.new(man.to_json, validate: validate) do |reader|
    ttl = RDF::Turtle::Writer.buffer(
      prefixes: {
        "":     "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/http-rdf-update/manifest#",
        cnt:    "http://www.w3.org/2011/content#",
        dawg:   "http://www.w3.org/2001/sw/DataAccess/tests/test-dawg#",
        ht:     "http://www.w3.org/2011/http#",
        mf:     "http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#",
        qt:     "http://www.w3.org/2001/sw/DataAccess/tests/test-query#",
        rdf:    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        rdfs:   "http://www.w3.org/2000/01/rdf-schema#",
      },
      base_uri: "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/manifest"
    ) {|writer| writer << reader}

    validate(RDF::Turtle::Reader.new(ttl, base_uri: "https://w3c.github.io/rdf-tests/sparql/sparql11/http-rdf-update/manifest", validate: true)) if validate

    # Do some result hacking
    ttl.sub!(/mf:entries \((.*)\) \.$/) do |matched|
      matched.sub('(<', '( <').gsub(' <', "\n    <")
    end
    
    output.write(ttl)
  end
else
  STDERR.puts "unknown output format #{format}"
  usage
end


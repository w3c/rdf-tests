# Build generated files
require 'rdf/turtle'
require 'json/ld'
require 'haml'
require 'htmlbeautifier'
require 'nokogiri'
require 'rake/clean'
require 'pathname'

# Test data and reports are UTF-8. Without this, a build running under a POSIX
# locale reads them as US-ASCII and dies on the first non-ASCII byte.
Encoding.default_external = Encoding::UTF_8

task default: [:index, :reports]

BASE_URI = 'https://w3c.github.io/rdf-tests/'

# Shared by every implementation report; see `implementation_report` below.
REPORT_TEMPLATE = 'report-template.haml'

# A reports directory holds EARL reports and their rollup, not test manifests,
# so nothing in one gets an HTML/JSON-LD rendering.
MANIFESTS = Dir.glob("**/manifest*.ttl").
  reject {|f| f.include?('-az') || f.split('/').include?('reports')}

SPECS = {
  "rdf-concepts/spec/index.html"  => "FIXME",
  "rdf-n-quads/spec/index.html"   => "rdf/rdf12/rdf-n-quads/",
  "rdf-n-triples/spec/index.html" => "rdf/rdf12/rdf-n-triples/",
  "rdf-schema/spec/index.html"    => "FIXME",
  "rdf-semantics/spec/index.html" => "rdf/rdf12/rdf-semantics/",
  "rdf-trig/spec/index.html"      => "rdf/rdf12/rdf-trig/",
  "rdf-turtle/spec/index.html"    => "rdf/rdf12/rdf-turtle/",
  "rdf-xml/spec/index.html"       => "rdf/rdf12/rdf-xml/",

  "sparql-concepts/spec/index.html"             => "",
  "sparql-entailment/spec/index.html"           => "",
  "sparql-federated-query/spec/index.html"      => "",
  "sparql-graph-store-protocol/spec/index.html" => "",
  "sparql-protocol/spec/index.html"             => "",
  "sparql-query/spec/index.html"                => "",
  "sparql-results-csv-tsv/spec/index.html"      => "",
  "sparql-results-json/spec/index.html"         => "",
  "sparql-results-xml/spec/index.html"          => "",
  "sparql-service-description/spec/index.html"  => "",
  "sparql-update/spec/index.html"               => ""
}

JSON_STATE = {
                 :indent => "  ",
                  :space => " ",
           :space_before => "",
              :object_nl => "\n",
               :array_nl => "\n",
              :allow_nan => false,
             :ascii_only => false,
            :max_nesting => 100,
            :script_safe => false,
                 :strict => false,
                  :depth => 0,
  :buffer_initial_length => 1024
}

CLOBBER.include("test-map.json")
desc "Build map of test references"
file "test-map.json" do
  puts "Generate test-map.json"
  # Test map will be like the following:
  # {
  #   "rdf/rdf11/rdf-xml/index.html" => {
  #     "xmlbase-test001" => [
  #       "https://w3c.github.io/rdf-xml/spec/index.html#baseURIs-tests1"
  #     ]
  #   }
  # }
  test_map = {}
  failed = false
  SPECS.each do |spec, ts|
    spec = "https://w3c.github.io/#{spec}"
    ts = RDF::URI("https://w3c.github.io/rdf-tests/#{ts}")
    puts "  Spec: #{spec}"
    RDF::Util::File.open_file(spec) do |f|
      dom = Nokogiri::HTML.parse(f)
      # Extract each referenced test from the data-tests attribute
      dom.css("*[data-tests]").each do |el|
        id = el['id']
        raise StandardError, "In #{spec}, data-tests found on element without an anchor" unless id

        el.attributes['data-tests']
          .value
          .split(',')
          .map(&:strip)
          .each do |ref|

            man, anchor = ref.split('#')
            man = ts.join(man).to_s.sub('https://w3c.github.io/rdf-tests/', '')
            ((test_map[man] ||= {})[anchor] ||= []) << "#{spec}##{id}"
        end
      end
    end
    rescue IOError => e
      failed = true
      puts "Failed to open URL: #{e.message}"
    rescue StandardError => e
      failed = true
      puts "An error occurred: #{e.message}"
  end

  unless failed
    File.open("test-map.json", "w") do |f|
      f.write(test_map.to_json(JSON_STATE))
    end
  end
end

desc "Build HTML manifests"
task index: MANIFESTS.
  select {|m| File.exist?(m)}.
  map {|m| m.sub(/manifest(.*)\.ttl$/, 'index\1.html')}

MANIFESTS.each do |ttl|
  html = ttl.sub(/manifest(.*)\.ttl$/, 'index\1.html')
  jsonld = ttl.sub(/\.ttl$/, '.jsonld')
  base = 'https://w3c.github.io/rdf-tests/' + ttl.sub('manifest.ttl', '')

  # Find frame closest to file
  frame_path, template_path = nil, nil
  Pathname.new(ttl).ascend do |p|
    f = File.join(p, 'manifest-frame.jsonld')
    frame_path ||= f if File.exist?(f)

    t = File.join(p, 'template.haml')
    template_path ||= t if File.exist?(t)
  end
  frame_path ||= 'manifest-frame.jsonld'

  CLOBBER.include(jsonld)
  desc "Build #{jsonld}"
  file jsonld => [ttl, frame_path] do
    puts "Generate #{jsonld}"
    frame = JSON.parse(File.read(frame_path))
    ctx = {"@base" => base}
    frame["@context"] = ctx.merge(frame["@context"]) # insert pseudo-comment and base at the top of the context

    RDF::Reader.open(ttl, base_uri: base) do |reader|
      out = JSON::LD::Writer.buffer(frame: frame, base_uri: base, simple_compact_iris: true) do |writer|
        writer << reader
      end

      # We do some normalization
      man = JSON.parse(out)
      if man.key?('@graph')
        Kernel.abort "Expected #{jsonld} to not have a single @graph entry"
      end

      # Fix up test entries
      Array(man['entries']).each do |entry|
        # Fix results which aren't IRIs
        if res = entry['mf:result'] && entry['mf:result']['@value']
          entry.delete('mf:result')
          entry['result'] = res == 'true'
        end

        # Fix some empty arrays (rdf-mt)
        %w(recognizedDatatypes unrecognizedDatatypes).each do |p|
          if entry["mf:#{p}"].is_a?(Hash) && entry["mf:#{p}"]['@list'] == []
            entry[p] = []
            entry.delete("mf:#{p}")
          end
        end
      end

      File.open(jsonld, "w") do |f|
        f.write(JSON::LD::API.serializer(man))
      end
    end
  end

  if template_path
    CLOBBER.include(html)
    desc "Build #{html}"
    file html => [jsonld, template_path, 'test-map.json'] do
      puts "Generate #{html}"
      template, man = File.read(template_path), nil

      man = JSON.parse(File.read(jsonld))
      if man.key?('@graph')
        Kernel.abort "Expected #{jsonld} to not have a single @graph entry"
      end

      haml_runner = if Haml::VERSION >= "6"
        Haml::Template.new(format: :html5) {template}
      else
        Haml::Engine.new(template, format: :html5)
      end

      File.open(html, "w") do |f|
        rendered = haml_runner.render(self,
            man: man,
            haml_indent: true,
            ttl: ttl.split('/').last,
            test_map: JSON.parse(File.read('test-map.json')).fetch(html, {})
          )
        beautified = HtmlBeautifier.beautify(rendered) + "\n"
        f.write(beautified)
      end
    end
  end
end

MF_INCLUDE = RDF::URI("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#include")

# Defines the tasks rolling the individual EARL reports in a report directory up
# into one implementation report, covering every test manifest reachable from
# the suite's top-level manifest. Returns the report to build.
def implementation_report(dir, suite)
  suite_dir  = File.dirname(dir)
  manifests  = "#{dir}/manifests.ttl"
  earl       = "#{dir}/earl.jsonld"
  html       = "#{dir}/index.html"
  assertions = Dir.glob("#{dir}/*.ttl").reject {|f| f == manifests}.sort

  CLOBBER.include(manifests)
  desc "Build #{manifests}"
  file manifests => MANIFESTS.grep(%r{^#{suite_dir}/}) do
    puts "Generate #{manifests}"
    graph = RDF::Graph.new
    visited, queue = Set.new, ["#{BASE_URI}#{suite_dir}/manifest.ttl"]
    until queue.empty?
      url = queue.shift
      next unless visited.add?(url)
      # Read from the working tree, but keep the published URL as base so that
      # test IRIs match the ones the individual EARL reports assert against.
      manifest = RDF::Graph.load(url.sub(BASE_URI, ''), base_uri: url, unique_bnodes: true)

      # Follow this manifest's mf:include lists to find any nested manifests
      manifest.query([nil, MF_INCLUDE, nil]).each do |stmt|
        RDF::List.new(subject: stmt.object, graph: manifest).each do |item|
          queue << item.to_s if item.uri?
        end
      end
      graph.insert(manifest)
    end

    # Stream rather than pretty-print: ordering 10k statements for nested bnode
    # syntax takes minutes, and nothing reads this file by hand.
    RDF::Turtle::Writer.open(manifests, stream: true, unique_bnodes: true) {|w| w << graph}
  end

  CLOBBER.include(earl)
  desc "Build #{earl}"
  file earl => [manifests] + assertions do
    require 'earl_report'
    puts "Generate #{earl}"
    # Run from the report directory so that the report links to its sources
    # relative to where they are published.
    Dir.chdir(dir) do
      report = EarlReport.new(*assertions.map {|f| File.basename(f)},
                              manifest: [File.basename(manifests)],
                              name: suite)
      File.open(File.basename(earl), "w") {|f| report.generate(format: :json, io: f)}
    end
  end

  CLOBBER.include(html)
  desc "Build #{html}"
  file html => [earl, REPORT_TEMPLATE] do
    require 'earl_report'
    puts "Generate #{html}"
    report = EarlReport.new(earl, json: true)
    File.open(REPORT_TEMPLATE) do |template|
      File.open(html, "w") {|f| report.generate(format: :html, template: template, io: f)}
    end
  end

  html
end

REPORTS = {
  'rdf/rdf12/reports'       => 'RDF 1.2',
  'sparql/sparql12/reports' => 'SPARQL 1.2',
}.map {|dir, suite| implementation_report(dir, suite)}

desc "Build implementation reports"
task reports: REPORTS

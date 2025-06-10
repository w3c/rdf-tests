# Build generated files
require 'rdf/turtle'
require 'json/ld'
require 'haml'
require 'htmlbeautifier'
require 'nokogiri'
require 'rake/clean'
require 'pathname'

task default: :index

MANIFESTS = Dir.glob("**/manifest*.ttl").reject {|f| f.include?('-az')}

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

CLOBBER.include(MANIFESTS.map {|ttl| ttl.sub(/manifest(.*)\.ttl$/, 'index\1.html')})

MANIFESTS.each do |ttl|
  html = ttl.sub(/manifest(.*)\.ttl$/, 'index\1.html')
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

  if template_path
    desc "Build #{html}"
    file html => [ttl, frame_path, template_path, 'test-map.json'] do
      puts "Generate #{html}"
      frame, template, man = File.read(frame_path), File.read(template_path), nil

      ttl_path, ttl_file = File.dirname(ttl), File.basename(ttl)
      Dir.chdir(ttl_path) do
        RDF::Reader.open(ttl_file, base_uri: base) do |reader|
          out = JSON::LD::Writer.buffer(frame: JSON.parse(frame), base_uri: base, simple_compact_iris: true) do |writer|
            writer << reader
          end

          man = JSON.parse(out)
          if man.key?('@graph')
            Kernel.abort "Expected manifest to not have a single @graph entry"
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
        end
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

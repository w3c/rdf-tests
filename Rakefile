# Build generated files
require 'rdf/turtle'
require 'json/ld'

task default: :manifests_json

JSONLD = %w(
  nquads/manifest.jsonld
  ntriples/manifest.jsonld
  rdf-mt/manifest.jsonld
  trig/manifest.jsonld
  turtle/manifest.jsonld

  sparql11/data-r2/manifest-evaluation.jsonld
  sparql11/data-r2/manifest-syntax.jsonld
  sparql11/data-r2/algebra/manifest.jsonld
  sparql11/data-r2/ask/manifest.jsonld
  sparql11/data-r2/basic/manifest.jsonld
  sparql11/data-r2/bnode-coreference/manifest.jsonld
  sparql11/data-r2/bound/manifest.jsonld
  sparql11/data-r2/cast/manifest.jsonld
  sparql11/data-r2/construct/manifest.jsonld
  sparql11/data-r2/dataset/manifest.jsonld
  sparql11/data-r2/distinct/manifest.jsonld
  sparql11/data-r2/expr-builtin/manifest.jsonld
  sparql11/data-r2/expr-equals/manifest.jsonld
  sparql11/data-r2/expr-ops/manifest.jsonld
  sparql11/data-r2/graph/manifest.jsonld
  sparql11/data-r2/i18n/manifest.jsonld
  sparql11/data-r2/open-world/manifest.jsonld
  sparql11/data-r2/optional/manifest.jsonld
  sparql11/data-r2/optional-filter/manifest.jsonld
  sparql11/data-r2/reduced/manifest.jsonld
  sparql11/data-r2/regex/manifest.jsonld
  sparql11/data-r2/solution-seq/manifest.jsonld
  sparql11/data-r2/sort/manifest.jsonld
  sparql11/data-r2/syntax-sparql1/manifest.jsonld
  sparql11/data-r2/syntax-sparql2/manifest.jsonld
  sparql11/data-r2/syntax-sparql3/manifest.jsonld
  sparql11/data-r2/syntax-sparql4/manifest.jsonld
  sparql11/data-r2/syntax-sparql5/manifest.jsonld
  sparql11/data-r2/triple-match/manifest.jsonld
  sparql11/data-r2/type-promotion/manifest.jsonld
  
  sparql11/data-sparql11/manifest-all.jsonld
  sparql11/data-sparql11/add/manifest.jsonld
  sparql11/data-sparql11/aggregates/manifest.jsonld
  sparql11/data-sparql11/basic-update/manifest.jsonld
  sparql11/data-sparql11/bind/manifest.jsonld
  sparql11/data-sparql11/bindings/manifest.jsonld
  sparql11/data-sparql11/clear/manifest.jsonld
  sparql11/data-sparql11/construct/manifest.jsonld
  sparql11/data-sparql11/copy/manifest.jsonld
  sparql11/data-sparql11/csv-tsv-res/manifest.jsonld
  sparql11/data-sparql11/delete/manifest.jsonld
  sparql11/data-sparql11/delete-data/manifest.jsonld
  sparql11/data-sparql11/delete-insert/manifest.jsonld
  sparql11/data-sparql11/delete-where/manifest.jsonld
  sparql11/data-sparql11/drop/manifest.jsonld
  sparql11/data-sparql11/entailment/manifest.jsonld
  sparql11/data-sparql11/exists/manifest.jsonld
  sparql11/data-sparql11/functions/manifest.jsonld
  sparql11/data-sparql11/grouping/manifest.jsonld
  sparql11/data-sparql11/http-rdf-update/manifest.jsonld
  sparql11/data-sparql11/json-res/manifest.jsonld
  sparql11/data-sparql11/move/manifest.jsonld
  sparql11/data-sparql11/negation/manifest.jsonld
  sparql11/data-sparql11/project-expression/manifest.jsonld
  sparql11/data-sparql11/property-path/manifest.jsonld
  sparql11/data-sparql11/protocol/manifest.jsonld
  sparql11/data-sparql11/service/manifest.jsonld
  sparql11/data-sparql11/service-description/manifest.jsonld
  sparql11/data-sparql11/subquery/manifest.jsonld
  sparql11/data-sparql11/syntax-fed/manifest.jsonld
  sparql11/data-sparql11/syntax-query/manifest.jsonld
  sparql11/data-sparql11/syntax-update-1/manifest.jsonld
  sparql11/data-sparql11/syntax-update-2/manifest.jsonld
  sparql11/data-sparql11/update-silent/manifest.jsonld
)
desc "Build manifests"
task manifests_json: JSONLD

JSONLD.each do |m|
  ttl = m.sub('.jsonld', '.ttl')
  # Find frame closest to file
  frame, exe = nil, nil
  Pathname.new(m).ascend do |p|
    f = File.join(p, 'manifest-frame.jsonld')
    frame ||= f if File.exist?(f)
    e = File.join(p, 'manifest-post')
    exe ||= e if File.executable?(e)
  end
  frame ||= 'manifest-frame.jsonld'

  file m => [ttl, frame] do
    puts "Genrate #{m}"
    RDF::Reader.open(ttl) do |reader|
      out = JSON::LD::Writer.buffer(frame: frame, simple_compact_iris: true) do |writer|
        writer << reader
      end

      man = JSON.parse(out)
      if man['@graph'].is_a?(Array) && man['@graph'].length == 1
        # Remove '@graph'
        man['@graph'][0].each do |k, v|
          man[k] = v
        end
        man.delete('@graph')

        # Remove nil 'entries'
        man.delete('mf:entries') if man['mf:entries'].nil?

        # Replace .ttl includes with .jsonld includes
        if man['include'].is_a?(Array)
          man['include'] = man['include'].map {|i| i.sub('.ttl', '.jsonld')}
        end
      else
        Kernel.abort "Expected manifest to have a single @graph entry"
      end
      File.open(m, "w") {|f| f.puts man.to_json(JSON::LD::JSON_STATE)}
    end

    # If there is a post-processing script, run it
    system exe, m, m if exe
  end
end

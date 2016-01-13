# Build generated files
require 'rdf/turtle'
require 'json/ld'
require 'haml'

task default: :index

MANIFESTS = Dir.glob("**/manifest*.ttl")

desc "Build HTML manifests"
task index: MANIFESTS.
  select {|m| File.exist?(m)}.
  map {|m| m.sub(/manifest(.*)\.ttl$/, 'index\1.html')}

desc "Build JSON-LD manifests"
task manifests_jsonld: MANIFESTS.
  map {|m| m.sub('.ttl', '.jsonld')}

MANIFESTS.each do |ttl|
  jsonld = ttl.sub('.ttl', '.jsonld')
  html = ttl.sub(/manifest(.*)\.ttl$/, 'index\1.html')

  # Find frame closest to file
  frame, exe, template = nil, nil, nil
  Pathname.new(ttl).ascend do |p|
    f = File.join(p, 'manifest-frame.jsonld')
    frame ||= f if File.exist?(f)

    e = File.join(p, 'manifest-post')
    exe ||= e if File.executable?(e)

    t = File.join(p, 'template.haml')
    template ||= t if File.exist?(t)
  end
  frame ||= 'manifest-frame.jsonld'

  if template
    desc "Build #{html}"
    file html => [jsonld, template] do
      puts "Genrate #{html}"
      temp = File.read(template)
      man = ::JSON.load(File.read(jsonld))

      File.open(html, "w") do |f|
        f.write Haml::Engine.new(temp, format: :html5).
          render(self,
            man: man,
            ttl: ttl.split('/').last,
            jsonld: jsonld.split('/').last
          )
      end
    end
  end

  desc "Build #{jsonld}"
  file jsonld => [ttl, frame] do
    puts "Genrate #{jsonld}"
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
      File.open(jsonld, "w") {|f| f.puts man.to_json(JSON::LD::JSON_STATE)}
    end

    # If there is a post-processing script, run it
    system exe, jsonld, jsonld if exe
  end
end

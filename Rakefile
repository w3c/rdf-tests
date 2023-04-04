# Build generated files
require 'rdf/turtle'
require 'json/ld'
require 'haml'
require 'htmlbeautifier'

task default: :index

MANIFESTS = Dir.glob("**/manifest*.ttl") - %w(rdf-mt/manifest-az.ttl)

desc "Build HTML manifests"
task index: MANIFESTS.
  select {|m| File.exist?(m)}.
  map {|m| m.sub(/manifest(.*)\.ttl$/, 'index\1.html')}

MANIFESTS.each do |ttl|
  html = ttl.sub(/manifest(.*)\.ttl$/, 'index\1.html')

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
    file html => [ttl, frame_path, template_path] do
      puts "Generate #{html}"
      frame, template, man = File.read(frame_path), File.read(template_path), nil

      ttl_path, ttl_file = File.dirname(ttl), File.basename(ttl)
      Dir.chdir(ttl_path) do
        RDF::Reader.open(ttl_file, base_uri: '') do |reader|
          out = JSON::LD::Writer.buffer(frame: JSON.parse(frame), simple_compact_iris: true) do |writer|
            writer << reader
          end

          man = JSON.parse(out)
          if man.key?('@graph')
            Kernel.abort "Expected manifest to have a single @graph entry"
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

      File.open(html, "w") do |f|
        rendered = Haml::Template.new {template}.
          render(self,
            man: man,
            haml_indent: true,
            ttl: ttl.split('/').last
          )
        beautified = HtmlBeautifier.beautify(rendered)
        f.write(beautified)
      end
    end
  end
end

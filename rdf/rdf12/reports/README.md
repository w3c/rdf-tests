This is a collection of individual
[EARL reports](https://www.w3.org/TR/EARL10-Schema/) for
test subjects claiming conformance to RDF 1.2 specifications.

The consolidated report is saved to `index.html` generated
using the
[earl-report Ruby gem](https://rubygems.org/gems/earl-report).
Run it as follows within this directory:

```sh
$ pushd ..; bundle install; popd
$ gem install earl-report
$ rm -f manifests.ttl && (pushd ..; rake reports/manifests.ttl; popd)
$ earl-report --format json -o earl.jsonld *.ttl --manifest manifests.ttl
$ earl-report --json --format html --template template.haml -o index.html earl.jsonld
```

#!/usr/bin/bash
#
# Script that generates the HTML manifests and reports based on the TTL files,
# as performed by the github action.
#
# DO NOT commit the generated files to the repository.

set -e

IMAGE=rdf-test-automations

cd "$(dirname "$0")"
cp ../Gemfile ../Gemfile.lock . # 'docker build' refuses to access parent dir
docker image rm -f $IMAGE
docker build -t $IMAGE .
docker run -v $PWD/..:/app --rm $IMAGE "$@"


#!/bin/bash
# vim: noexpandtab
set -o errexit
set -o verbose

mkdir build
cp ../base/risecamp_start.sh build

for proj in clipper example flor integration opaque pywren ray wave; do
	tag="ucbrise/risecamp2018-$proj"

	# generate patched image
	cat > build/Dockerfile <<-EOF
		FROM $tag:source
		COPY ./risecamp_start.sh /opt
	EOF
	docker build --tag="$tag:latest" build/
	rm build/Dockerfile

	# push to hub
	docker push "$tag:latest"
done

rm build/risecamp_start.sh
rmdir build

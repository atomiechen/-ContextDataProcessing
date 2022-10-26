#!/bin/sh

## docker compose usage
# docker-compose run --rm elasticdump $@

## command line usage
docker run --rm -it \
	--net=host \
	-v $(pwd):/data \
	-w /data \
	-e NODE_TLS_REJECT_UNAUTHORIZED=0 \
	--entrypoint $(dirname $0)/command.sh \
	elasticdump/elasticsearch-dump \
	$@

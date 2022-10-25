#!/bin/sh

## docker compose usage
# docker-compose run --rm elasticdump

## command line usage
docker run --rm -it \
	--name=context-elasticdump \
	--net=host \
	-v $(pwd):/data \
	-w /data \
	-e NODE_TLS_REJECT_UNAUTHORIZED=0 \
	elasticdump/elasticsearch-dump \
	./command.sh

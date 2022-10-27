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


# ## docker run one-command usage below

# ## set username and password
# ## or use `--httpAuthFile=config_auth` if only 1 remote ES
# set -a # automatically export all variables
# . $(dirname $0)/config_auth
# set +a

# docker run --rm -it \
# 	--net=host \
# 	-v $(pwd):/data \
# 	-w /data \
# 	-e NODE_TLS_REJECT_UNAUTHORIZED=0 \
# 	elasticdump/elasticsearch-dump \
# 	--input=https://$user:$password@localhost:29500/log_volume \
# 	--output "$@" \
# 	--type=data \
# 	--searchBody=@$(dirname $0)/searchbody.json \
# 	--sourceOnly \
# 	--limit=10000 \
# 	--fileSize=100mb \
# 	--csvIgnoreAutoColumns=true \

#!/bin/sh

## set username and password
## or use `--httpAuthFile=config_auth` if only 1 remote ES
set -a # automatically export all variables
. $(dirname $0)/config_auth
set +a

elasticdump \
	--input=https://$user:$password@localhost:29500/log_volume \
	--output "$@" \
	--type=data \
	--searchBody=@$(dirname $0)/searchbody.json \
	--sourceOnly \
	--limit=10000 \
	--fileSize=100mb \
	--csvIgnoreAutoColumns=true \
	# --searchBody="{\"query\":{\"term\":{\"userid\": \"userid_test_userid\"}}}" \

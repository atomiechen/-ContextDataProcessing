#!/bin/sh

## set username and password
## or use `--httpAuthFile=config_auth` if only 1 remote ES
set -a # automatically export all variables
. ./config_auth
set +a

elasticdump \
	--input=https://$user:$password@localhost:29500/log_volume \
	--output=download.ndjson --overwrite \
	--type=data \
	--searchBody="{\"query\":{\"term\":{\"userid\": \"userid_test_userid\"}}}" \

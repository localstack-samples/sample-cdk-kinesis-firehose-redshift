export AWS_ACCESS_KEY_ID ?= test
export AWS_SECRET_ACCESS_KEY ?= test
export AWS_DEFAULT_REGION=us-east-1
SHELL := /bin/bash

usage:		## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$//' | sed -e 's/##//'

install:	## Install dependencies
	@which lstk || npm install -g @localstack/lstk aws-cdk

start:		## Start LocalStack
	@test -n "${LOCALSTACK_AUTH_TOKEN}" || (echo "LOCALSTACK_AUTH_TOKEN is not set. Find your token at https://app.localstack.cloud/workspace/auth-token"; exit 1)
	@LOCALSTACK_AUTH_TOKEN=$(LOCALSTACK_AUTH_TOKEN) lstk start

stop:		## Stop LocalStack
	@lstk stop

logs:		## Save the logs in a separate file
	@lstk logs > logs.txt

.PHONY: usage install start stop logs deploy-localstack deploy-aws

deploy-localstack:
	@echo "Preparing deployment"
	lstk cdk bootstrap
	lstk cdk synth
	@echo "Deploy redshift stack"
	lstk cdk deploy KinesisFirehoseRedshiftStack1 --require-approval never
	python utils/prepare_redshift.py
	@echo "Deploy firehose stack"
	lstk cdk deploy KinesisFirehoseRedshiftStack2 --require-approval never

list-resources-localstack:
	@echo "List resources"
	lstk aws s3 ls
	lstk aws kinesis list-streams
	lstk aws firehose list-delivery-streams
	lstk aws redshift describe-clusters

deploy-aws:
	@echo "Preparing deployment"
	cdk bootstrap
	cdk synth
	@echo "Deploy redshift stack"
	cdk deploy KinesisFirehoseRedshiftStack1 --require-approval never
	python utils/prepare_redshift.py
	@echo "Deploy firehose stack"
	cdk deploy KinesisFirehoseRedshiftStack2 --require-approval never

start-producer:
	python utils/producer_kinesis.py

start-localstack:
	@docker ps -f "name=localstack" | grep localstack > /dev/null || (echo "Starting localstack..." && lstk start)

test:
	pytest -v
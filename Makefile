export AWS_ACCESS_KEY_ID ?= test
export AWS_SECRET_ACCESS_KEY ?= test
export AWS_DEFAULT_REGION=us-east-1
SHELL := /bin/bash

usage:		## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$//' | sed -e 's/##//'

install:	## Install dependencies
	@which localstack || pip install localstack
	@which awslocal || pip install awscli-local
	@which cdklocal || npm install -g aws-cdk-local aws-cdk

start:		## Start LocalStack
	@test -n "${LOCALSTACK_AUTH_TOKEN}" || (echo "LOCALSTACK_AUTH_TOKEN is not set. Find your token at https://app.localstack.cloud/workspace/auth-token"; exit 1)
	@LOCALSTACK_AUTH_TOKEN=$(LOCALSTACK_AUTH_TOKEN) localstack start -d

stop:		## Stop LocalStack
	@localstack stop

ready:		## Wait until LocalStack is ready
	@echo Waiting on the LocalStack container...
	@localstack wait -t 30 && echo LocalStack is ready to use! || (echo Gave up waiting on LocalStack, exiting. && exit 1)

logs:		## Save the logs in a separate file
	@localstack logs > logs.txt

.PHONY: usage install start stop ready logs deploy-localstack deploy-aws

deploy-localstack:
	@echo "Preparing deployment"
	cdklocal bootstrap
	cdklocal synth
	@echo "Deploy redshift stack"
	cdklocal deploy KinesisFirehoseRedshiftStack1 --require-approval never
	python utils/prepare_redshift.py
	@echo "Deploy firehose stack"
	cdklocal deploy KinesisFirehoseRedshiftStack2 --require-approval never

list-resources-localstack:
	@echo "List resources"
	awslocal s3 ls
	awslocal kinesis list-streams
	awslocal firehose list-delivery-streams
	awslocal redshift describe-clusters

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
	@docker ps -f "name=localstack" | grep localstack > /dev/null || (echo "Starting localstack..." && localstack start)

test:
	pytest -v
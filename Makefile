.PHONY: deploy-localstack deploy-aws

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
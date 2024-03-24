deploy-localstack:
	@echo "Preparing deployment"
	cdklocal bootstrap
	cdklocal synth
	@echo "Deploy redshift stack"
	cdklocal deploy KinesisFirehoseRedshiftStack1 --require-approval never
	source .venv/bin/activate &&  python utils/prepare_redshift.py
	@echo "Deploy firehose stack"
	cdklocal deploy KinesisFirehoseRedshiftStack2 --require-approval never

deploy-aws:
	@echo "Preparing deployment"
	cdk bootstrap
	cdk synth
	@echo "Deploy redshift stack"
	cdk deploy KinesisFirehoseRedshiftStack1 --require-approval never
	source .venv/bin/activate &&  python utils/prepare_redshift.py
	@echo "Deploy firehose stack"
	cdk deploy KinesisFirehoseRedshiftStack2 --require-approval never

start-producer:
	source .venv/bin/activate && python utils/producer_kinesis.py

start-localstack:
	@docker ps -f "name=localstack" | grep localstack > /dev/null || (echo "Starting localstack..." && localstack start)

test:
	source .venv/bin/activate && pytest -v
import aws_cdk as cdk

from stacks.KinesisFirehoseRedshiftStack1 import KinesisFirehoseRedshiftStack1
from stacks.KinesisFirehoseRedshiftStack2 import KinesisFirehoseRedshiftStack2

app = cdk.App()

# define required access roles and resources (kinesis, s3, vpc, redshift) 
# except firehose in stack 1
stack_1 = KinesisFirehoseRedshiftStack1(app, "KinesisFirehoseRedshiftStack1")

# define firehose and source / target definitions in stack 2
# due to bug with resolving Endpoint.Address of the redshift cluster,
# this needs to be in a separate stack.
# see issue: https://github.com/aws/aws-cdk/discussions/29355
stack_2 = KinesisFirehoseRedshiftStack2(
    app,
    "KinesisFirehoseRedshiftStack2",
    kinesis_stream_arn=stack_1.kinesis_stream.stream_arn,
    role_firehose_kinesis_arn=stack_1.role_firehose_kinesis.role_arn,
    role_firehose_s3_arn=stack_1.role_firehose_s3.role_arn,
    firehose_s3_log_group_name=stack_1.firehose_s3_log_group_name,
    firehose_s3_log_stream_name=stack_1.firehose_s3_log_stream_name,
    bucket_arn=stack_1.bucket.bucket_arn,
    cluster_address=stack_1.redshift_cluster.attr_endpoint_address,
    cluster_port=stack_1.redshift_cluster.attr_endpoint_port,
)

app.synth()

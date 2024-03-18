import os
import sys

import aws_cdk as cdk
import aws_cdk.aws_kinesisfirehose as firehose
from constructs import Construct
from dotenv import load_dotenv

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from data.sample_data import sample_user_dtypes

# Load environment variables from .env file
load_dotenv()

# Access the variables using os.environ
redshift_master_user = os.environ.get("REDSHIFT_MASTER_USER")
redshift_master_password = os.environ.get("REDSHIFT_MASTER_PASSWORD")
redshift_db_name = os.environ.get("REDSHIFT_DB_NAME")
redshift_table_name = os.environ.get("REDSHIFT_TABLE_NAME")


class KinesisFirehoseRedshiftStack2(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        id: str,
        kinesis_stream_arn: str,
        role_firehose_kinesis_arn: str,
        role_firehose_s3_arn: str,
        firehose_s3_log_group_name: str,
        firehose_s3_log_stream_name: str,
        bucket_arn: str,
        cluster_address: str,
        cluster_port: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        kinesis_stream_source_configuration = (
            firehose.CfnDeliveryStream.KinesisStreamSourceConfigurationProperty(
                kinesis_stream_arn=kinesis_stream_arn,
                role_arn=role_firehose_kinesis_arn,
            )
        )

        redshift_s3_destination_configuration = firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
            bucket_arn=bucket_arn,
            role_arn=role_firehose_s3_arn,
            prefix="redshift-raw-data/",
            # error_output_prefix="firehose-raw-data/errors/", # not yet supported by AWS although in the documentation
            compression_format="UNCOMPRESSED",
            buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                interval_in_seconds=1, size_in_m_bs=1
            ),
            encryption_configuration=firehose.CfnDeliveryStream.EncryptionConfigurationProperty(
                no_encryption_config="NoEncryption"
            ),
            cloud_watch_logging_options=firehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                enabled=True,
                log_group_name=firehose_s3_log_group_name,
                log_stream_name=firehose_s3_log_stream_name,
            ),
        )
        redshift_destination_configuration = firehose.CfnDeliveryStream.RedshiftDestinationConfigurationProperty(
            cluster_jdbcurl=f"jdbc:redshift://{cluster_address}:{cluster_port}/{redshift_db_name}",
            copy_command=firehose.CfnDeliveryStream.CopyCommandProperty(
                data_table_name=redshift_table_name,
                copy_options="json 'auto' blanksasnull emptyasnull",
                # for reference of copy command options https://docs.aws.amazon.com/redshift/latest/dg/r_COPY_command_examples.html#r_COPY_command_examples-copy-from-json
                # MANIFEST json 'auto' TRUNCATECOLUMNS blanksasnull emptyasnull;",
                data_table_columns=f"{','.join(sample_user_dtypes.keys())}",
                # keys in json file from keys in kinesis input must be lower case
            ),
            password=redshift_master_password,
            username=redshift_master_user,
            role_arn=role_firehose_s3_arn,
            s3_configuration=redshift_s3_destination_configuration,
            cloud_watch_logging_options=firehose.CfnDeliveryStream.CloudWatchLoggingOptionsProperty(
                enabled=True,
                log_group_name=firehose_s3_log_group_name,
                log_stream_name=firehose_s3_log_stream_name,
            ),
        )

        firehose_stream = firehose.CfnDeliveryStream(
            self,
            "FirehoseDeliveryStreamNew",
            delivery_stream_name="firehose-deliverystream-new",
            delivery_stream_type="KinesisStreamAsSource",
            kinesis_stream_source_configuration=kinesis_stream_source_configuration,
            redshift_destination_configuration=redshift_destination_configuration,
        )

        # specify outputs
        cdk.CfnOutput(
            self,
            "FirehoseDeliveryStreamName",
            value=firehose_stream.delivery_stream_name,
        )

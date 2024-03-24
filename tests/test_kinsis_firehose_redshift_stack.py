import json
import os
import sys

import boto3
from dotenv import load_dotenv

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir)

from data.sample_data import sample_users
from utils.helper_methods import (
    get_expected_data_from_redshift_table,
    get_redshift_endpoint,
)

load_dotenv()

redshift_db_name = os.getenv("REDSHIFT_DB_NAME")
redshift_master_user = os.getenv("REDSHIFT_MASTER_USER")
redshift_master_password = os.getenv("REDSHIFT_MASTER_PASSWORD")
redshift_table_name = os.getenv("REDSHIFT_TABLE_NAME")
redshift_cluster_name = os.environ.get("REDSHIFT_CLUSTER_NAME")

kinesis_stream_name = os.getenv("KINESIS_STREAM_NAME")

cluster_address, cluster_port = get_redshift_endpoint(redshift_cluster_name)


def test_kinesis_firehose_redshift_stack():
    kinesis_client = boto3.client("kinesis")

    # send data to kinesis stream
    for sample_user in sample_users:
        response = kinesis_client.put_record(
            StreamName=kinesis_stream_name,
            Data=json.dumps(sample_user),
            PartitionKey="1",
        )
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # read data from redshift table
    connection_string = f"dbname={redshift_db_name} user={redshift_master_user} password={redshift_master_password} host={cluster_address} port={cluster_port}"
    sql_query = f"SELECT * FROM {redshift_table_name}"  # vulnerable to SQL injection dont use in production

    df_user_health_data = get_expected_data_from_redshift_table(
        connection_string, sql_query, len(sample_users), retries=30, sleep=10
    )

    # cast pandas timestamp to string and compare with sample_users
    assert [
        {**item, "timestamp": item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")}
        for item in df_user_health_data.to_dict("records")
    ] == sample_users

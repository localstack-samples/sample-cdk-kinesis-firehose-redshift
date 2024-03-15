import random
import time
from pathlib import Path
from typing import Callable, TypeVar

import boto3
import pandas as pd
import psycopg2
from dotenv import load_dotenv

env_path = Path("..") / ".env"
load_dotenv(env_path)


def get_redshift_endpoint(cluster_name):
    """
    Get the endpoint address and port of the Redshift cluster
    """
    redshift_client = boto3.client("redshift")

    clusters_response = redshift_client.describe_clusters()
    for cluster in clusters_response["Clusters"]:
        if cluster["ClusterIdentifier"] == cluster_name:
            address = cluster["Endpoint"]["Address"]
            port = cluster["Endpoint"]["Port"]

            return address, port


def create_table_sql_generator(table_name, dtypes_dict):
    """
    Generate the SQL command to create a table with the given name
    and column definitions extracted from columns type dictionary
    """
    # Generate column definitions string
    columns_sql = ",\n".join(
        [f"{column} {dtype}" for column, dtype in dtypes_dict.items()]
    )
    # Create the full CREATE TABLE SQL string
    create_table_sql = f"CREATE TABLE {table_name} (\n{columns_sql}\n);"
    return create_table_sql


def redshift_connection_handler(connection_string, sql_command):
    """
    Execute the given SQL command on the Redshift cluster
    """
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(sql_command)
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "command executed successfully", "status_code": 200}
    except Exception as e:
        # Assuming 500 as a generic server error status code for any exception
        return {"status": "error", "error": str(e), "status_code": 500}


def get_new_messages(sample_users):
    messages = []
    for user in sample_users:
        message = user.copy()
        message["hr_value"] = random.randint(60, 180)
        message["novel_stress_marker"] = round(random.uniform(10, 200), 2)
        message["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        messages.append(message)
    return messages


def redshift_read_table(connection_string, sql_query):
    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        records = pd.read_sql(sql_query, conn)
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        return {"status": "error", "error": str(e)}


T = TypeVar("T")


def retry(
    function: Callable[..., T], retries=3, sleep=1.0, sleep_before=0, **kwargs
) -> T:
    raise_error = None
    if sleep_before > 0:
        time.sleep(sleep_before)
    retries = int(retries)
    for i in range(0, retries + 1):
        try:
            return function(**kwargs)
        except Exception as error:
            raise_error = error
            time.sleep(sleep)
    raise raise_error


def get_expected_data_from_redshift_table(
    connection_string: str,
    sql_query: str,
    expected_row_count: int,
    retries: int = 30,
    sleep: int = 10,
) -> pd.DataFrame:
    def get_data():
        df = redshift_read_table(connection_string, sql_query)
        if df.shape[0] != expected_row_count:
            raise Exception(f"Failed to receive all expected rows: {df}")
        else:
            return df

    return retry(get_data, retries, sleep)


def read_s3_data(s3_client, bucket_name: str) -> dict[str, str]:
    response = s3_client.list_objects(Bucket=bucket_name)
    if response.get("Contents") is None:
        raise Exception("No data in bucket yet")

    keys = [obj.get("Key") for obj in response.get("Contents")]

    bucket_data = dict()
    for key in keys:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        data = response["Body"].read().decode("utf-8")
        bucket_data[key] = data
    return bucket_data

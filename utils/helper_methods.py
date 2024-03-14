import random
import time
from pathlib import Path

import boto3
import psycopg2
from dotenv import load_dotenv

env_path = Path("..") / ".env"
load_dotenv(env_path)


# get cluster endpoint address and port
def get_redshift_endpoint(cluster_name):
    redshift_client = boto3.client("redshift")

    clusters_response = redshift_client.describe_clusters()
    for cluster in clusters_response["Clusters"]:
        if cluster["ClusterIdentifier"] == cluster_name:
            address = cluster["Endpoint"]["Address"]
            port = cluster["Endpoint"]["Port"]

            return address, port


def create_table_sql_generator(table_name, dtypes_dict):
    # Generate column definitions string
    columns_sql = ",\n".join(
        [f"{column} {dtype}" for column, dtype in dtypes_dict.items()]
    )
    # Create the full CREATE TABLE SQL string
    create_table_sql = f"CREATE TABLE {table_name} (\n{columns_sql}\n);"
    return create_table_sql


def redshift_connection_handler(connection_string, sql_command):
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

import os
import sys

from dotenv import load_dotenv

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from data.sample_data import sample_user_dtypes
from utils.helper_methods import (
    create_table_sql_generator,
    get_redshift_endpoint,
    redshift_connection_handler,
)

load_dotenv()

redshift_master_user = os.environ.get("REDSHIFT_MASTER_USER")
redshift_master_password = os.environ.get("REDSHIFT_MASTER_PASSWORD")
redshift_db_name = os.environ.get("REDSHIFT_DB_NAME")
redshift_cluster_name = os.environ.get("REDSHIFT_CLUSTER_NAME")

redshift_table_name = os.environ.get("REDSHIFT_TABLE_NAME")

redshift_cluster_address, redshift_cluster_port = get_redshift_endpoint(
    redshift_cluster_name
)

# prepare redshift table
connection_string = f"dbname={redshift_db_name} user={redshift_master_user} password={redshift_master_password} host={redshift_cluster_address} port={redshift_cluster_port}"

create_table_sql = create_table_sql_generator(redshift_table_name, sample_user_dtypes)

response = redshift_connection_handler(connection_string, create_table_sql)
assert response["status_code"] == 200

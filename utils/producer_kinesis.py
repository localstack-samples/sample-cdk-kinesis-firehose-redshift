import json
import os
import sys
import time
import uuid

import boto3
from dotenv import load_dotenv

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from data.sample_data import sample_users
from utils.helper_methods import get_new_messages

load_dotenv()

kinesis_stream_name = os.environ.get("KINESIS_STREAM_NAME")

# insert into kinesis stream
kinesis_client = boto3.client("kinesis")

while True:
    short_uid = uuid.uuid4().hex[:8]
    messages = get_new_messages(sample_users)  # random data
    for message in messages:
        kinesis_client.put_record(
            StreamName=kinesis_stream_name,
            Data=json.dumps(message),
            PartitionKey="1",
        )
        print("Created 1 Kinesis record with for all sample users.")
    time.sleep(10)

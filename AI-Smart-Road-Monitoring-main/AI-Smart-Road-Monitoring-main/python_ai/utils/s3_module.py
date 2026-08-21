import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
from utils.logger import get_logger

logger = get_logger(__name__)

def upload_to_s3(bucket_name, file_path, key):
    s3 = boto3.client("s3")
    try:
        s3.upload_file(file_path, bucket_name, key)
        logger.info(f"Uploaded {file_path} to S3://{bucket_name}/{key}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")

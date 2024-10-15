import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, CredentialRetrievalError, ClientError
from typing import Optional

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME


def get_s3_client() -> Optional[boto3.client]:
    try:
        return boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
    except (NoCredentialsError, PartialCredentialsError, CredentialRetrievalError) as e:
        print("Error with AWS credentials: ", e)
        return None


def upload_file_to_s3(local_file_path, s3_file_name, user_id) -> bool:
    s3_client = get_s3_client()
    if not s3_client:
        print("Could not establish a connection to S3 due to credential issues.")
        return False

    try:
        s3_key = f"{user_id}/{s3_file_name}"
        s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_key)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except ClientError as e:
        print(f"Client error occurred: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def get_file_from_s3(s3_key) -> Optional[str]:
    s3_client = get_s3_client()
    if not s3_client:
        print("Could not establish a connection to S3 due to credential issues.")
        return None

    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return response['Body'].read()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"The object with key {s3_key} does not exist.")
        else:
            print(f"An error occurred: {e}")
        return None
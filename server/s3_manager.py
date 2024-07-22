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


def upload_file_to_s3(local_file_path, s3_file_name) -> bool:
    s3_client = get_s3_client()
    if not s3_client:
        print("Could not establish a connection to S3 due to credential issues.")
        return False

    try:
        s3_client.upload_file(local_file_path, S3_BUCKET_NAME, s3_file_name)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except ClientError as e:
        # Catch other boto3 client errors
        print(f"Client error occurred: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

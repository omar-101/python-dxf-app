import boto3
import uuid

REGION = "nyc3"  # Replace with your region
ENDPOINT_URL = "https://nyc3.digitaloceanspaces.com"
ACCESS_KEY = "DO801KLFJCCWANAW3XYA"
SECRET_KEY = "KDPGqv2ZwVtvfTdw7EWLmOG2oVcThXMBXtrlue67Zxk"
SPACE_NAME = "smartscale"
SPACE_URI = "https://smartscale.nyc3.digitaloceanspaces.com"

# Initialize client
session = boto3.session.Session()
client = session.client(
    "s3",
    region_name=REGION,
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


def upload_file(file_path):
    file_name = f"dxf-draws/{uuid.uuid4()}.png"

    client.upload_file(
        file_path,
        SPACE_NAME,
        file_name,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": "image/png",
        },
    )

    return f"{SPACE_URI}/{file_name}"

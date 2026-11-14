"""AWS Lambda Handler for CampusGPT.

Wraps the FastAPI application using Mangum.
Fetches secrets from AWS Secrets Manager on cold start rather than plaintext env vars.
Uses FAISS for in-memory vector search in /tmp.
"""

import os
import json
import logging
from mangum import Mangum

logger = logging.getLogger("campusgpt.aws")


def fetch_secret_if_in_aws(secret_name: str = "campusgpt/gemini_api_key", region_name: str = "us-east-1"):
    """Fetch Gemini API Key from AWS Secrets Manager on cold start."""
    # Only execute if running in an AWS Lambda environment
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return

    try:
        import boto3
        client = boto3.client("secretsmanager", region_name=region_name)
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            secret_data = json.loads(response["SecretString"])
            api_key = secret_data.get("GEMINI_API_KEY", "")
            if api_key:
                os.environ["GEMINI_API_KEY"] = api_key
                logger.info("Successfully loaded GEMINI_API_KEY from AWS Secrets Manager.")
    except Exception as e:
        logger.warning(f"Could not load secret from AWS Secrets Manager: {e}")


# Cold-start initialization
fetch_secret_if_in_aws()

# Ensure Lambda uses FAISS vector store backend
os.environ["VECTOR_STORE"] = "faiss"

# Import FastAPI app
from backend.app.main import app

# Mangum ASGI handler
handler = Mangum(app, lifespan="off")

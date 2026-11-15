"""AWS Lambda Handler for CampusGPT.

Wraps the FastAPI application using Mangum for serverless deployment.
On cold start:
  1. Fetches the Gemini API key from AWS Secrets Manager.
  2. Downloads the FAISS vector index from S3 into /tmp (Lambda's writable disk).
  3. Points the vector store at /tmp/vectorstore.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("campusgpt.lambda")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Cold-start Step 1: Load Gemini API Key from Secrets Manager
# ---------------------------------------------------------------------------
def fetch_secret(secret_name: str | None = None, region: str = "us-east-1") -> None:
    """Fetch Gemini API Key from AWS Secrets Manager and inject into env."""
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        # Not running in Lambda – local dev uses .env file
        return

    secret_name = secret_name or os.environ.get(
        "SECRET_NAME", "campusgpt/gemini_api_key"
    )
    region = os.environ.get("AWS_DEFAULT_REGION", region)

    try:
        import boto3
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(response["SecretString"])
        api_key = secret_data.get("GEMINI_API_KEY", "")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            logger.info("GEMINI_API_KEY loaded from Secrets Manager.")
        else:
            logger.warning("GEMINI_API_KEY key not found in secret JSON.")
    except Exception as exc:
        logger.error("Failed to load secret: %s", exc)


# ---------------------------------------------------------------------------
# Cold-start Step 2: Download FAISS index from S3 into /tmp
# ---------------------------------------------------------------------------
def download_faiss_from_s3() -> None:
    """Download FAISS index and metadata from S3 into Lambda's /tmp."""
    if not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return

    bucket = os.environ.get("S3_BUCKET", "")
    if not bucket:
        logger.warning("S3_BUCKET env var not set; skipping FAISS download.")
        return

    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    tmp_vs = Path("/tmp/vectorstore")
    tmp_vs.mkdir(parents=True, exist_ok=True)

    files_to_download = [
        ("vectorstore/faiss_index.bin", tmp_vs / "faiss_index.bin"),
        ("vectorstore/faiss_meta.json", tmp_vs / "faiss_meta.json"),
    ]

    try:
        import boto3
        s3 = boto3.client("s3", region_name=region)
        for s3_key, local_path in files_to_download:
            if not local_path.exists():
                logger.info("Downloading s3://%s/%s → %s", bucket, s3_key, local_path)
                s3.download_file(bucket, s3_key, str(local_path))
            else:
                logger.info("Already cached: %s", local_path)

        # Tell CampusGPT where to find the index
        os.environ["FAISS_INDEX_FILE"] = str(tmp_vs / "faiss_index.bin")
        os.environ["FAISS_META_FILE"] = str(tmp_vs / "faiss_meta.json")
        logger.info("FAISS index ready in /tmp/vectorstore.")
    except Exception as exc:
        logger.error("Failed to download FAISS index from S3: %s", exc)


# ---------------------------------------------------------------------------
# Cold-start initialisation (runs once per Lambda container lifetime)
# ---------------------------------------------------------------------------
fetch_secret()
download_faiss_from_s3()

# Force FAISS backend (Lambda has no ChromaDB SQLite support)
os.environ["VECTOR_STORE"] = "faiss"

# ---------------------------------------------------------------------------
# Import FastAPI app and wrap with Mangum
# ---------------------------------------------------------------------------
from backend.app.main import app  # noqa: E402  (must come after env setup)
from mangum import Mangum          # noqa: E402

handler = Mangum(app, lifespan="off")

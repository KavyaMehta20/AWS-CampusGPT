# CampusGPT — AWS Deployment Guide

> **Quick reference for the presenting team.** Full step-by-step guide is in the artifact or the Architecture PDF.

## What gets deployed

| AWS Resource | Purpose |
|---|---|
| **Lambda Function** | Runs the FastAPI backend (Mangum wrapper) |
| **HTTP API Gateway** | Public HTTPS endpoint → routes to Lambda |
| **S3 Bucket** | Stores the FAISS vector index |
| **Secrets Manager** | Holds the Gemini API key (never in code) |
| **CloudFormation Stack** | Manages all resources as one unit |

## Deployment checklist

- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] SAM CLI installed
- [ ] Docker Desktop running (for `--use-container` builds)
- [ ] Gemini key in Secrets Manager (`campusgpt/gemini_api_key`)
- [ ] FAISS index built (`python scripts/build_faiss_index.py`)
- [ ] `sam build --template deploy/aws/template.yaml --use-container`
- [ ] `sam deploy --template deploy/aws/template.yaml --guided`
- [ ] FAISS index files uploaded to S3
- [ ] Live endpoint tested

## Quick commands

```powershell
# From repo root
sam build --template deploy\aws\template.yaml --use-container
sam deploy

# Upload FAISS index after building
aws s3 cp vectorstore\faiss_index.bin s3://<BUCKET>/vectorstore/faiss_index.bin
aws s3 cp vectorstore\faiss_meta.json s3://<BUCKET>/vectorstore/faiss_meta.json

# Test
Invoke-RestMethod -Uri "https://<ID>.execute-api.us-east-1.amazonaws.com/health" -Method GET

# Teardown (after demo)
sam delete --stack-name campusgpt-stack
aws secretsmanager delete-secret --secret-id campusgpt/gemini_api_key --force-delete-without-recovery
```

## Files

| File | Purpose |
|---|---|
| `template.yaml` | AWS SAM/CloudFormation template |
| `lambda_handler.py` | Mangum wrapper + cold-start secret/FAISS loading |
| `../../requirements-lambda.txt` | Lambda-specific deps (faiss-cpu, no chromadb) |
| `../../scripts/build_faiss_index.py` | Builds FAISS index from documents |

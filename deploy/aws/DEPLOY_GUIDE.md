# AWS Deployment Guide for Presenter & Students (Slide 16)

> **IMPORTANT NOTICE:** This is a prepared, presenter-led demo template. Do not run deployments without an authorized AWS account and cost budget alerts enabled.

---

## Architecture Overview
- **Compute:** AWS Lambda running Python 3.11 with FastAPI wrapped in **Mangum**.
- **API Routing:** Amazon API Gateway (HTTP API).
- **Secrets Management:** `GEMINI_API_KEY` stored in **AWS Secrets Manager** (fetched once at cold start; never exposed in environment variables or code).
- **Vector Search:** In-memory **FAISS** index (`vectorstore/faiss_index.bin`) downloaded into Lambda's ephemeral `/tmp` storage. *(Note: ChromaDB is not used on Lambda because Chroma requires a persistent filesystem and local SQLite database).*

---

## 6-Step Presenter Demo

### Step 1: Inspect the AWS SAM Template
Open and walk students through [template.yaml](template.yaml):
- Show the least-privilege IAM policies.
- Explain why secrets are **not** hardcoded in template environment variables.

### Step 2: Build the FAISS Index
Before packaging, create the lightweight FAISS index:
```bash
python scripts/build_faiss_index.py
```

### Step 3: Configure Gemini API Key in Secrets Manager
Create the secret in your target AWS region:
```bash
aws secretsmanager create-secret \
    --name campusgpt/gemini_api_key \
    --secret-string '{"GEMINI_API_KEY":"YOUR_ACTUAL_GEMINI_KEY"}' \
    --region us-east-1
```

### Step 4: Build and Package with AWS SAM
```bash
sam build --use-container
```

### Step 5: Deploy the Stack
```bash
sam deploy --guided
```
Follow the interactive prompts (Stack Name: `campusgpt-stack`, Region: `us-east-1`, Confirm changes: `Y`).
Copy the resulting `HttpApiUrl` from the terminal output (e.g. `https://xyz123.execute-api.us-east-1.amazonaws.com`).

### Step 6: Test with Ready-to-Paste cURL
Test your deployed live API Gateway:
```bash
curl -X POST "https://<YOUR_API_GATEWAY_URL>/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the 11 courses in the common business core?"}'
```

---

## Clean-Up Instructions (Prevent Accidental AWS Charges)
To tear down all resources when the workshop finishes:
```bash
sam delete --stack-name campusgpt-stack
aws secretsmanager delete-secret --secret-id campusgpt/gemini_api_key --force-delete-without-recovery
```

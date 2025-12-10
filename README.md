# Vertex AI Agent Deployment Guide (README)

A clear and streamlined guide to help you authenticate, configure, and deploy your ADK-powered agent on Google Cloud using Vertex AI Agent Engine.

---

## 🚀 1. Authenticate Your Google Cloud Account

Ensure you're logged into a **billed Google Cloud account**.

```bash
gcloud auth application-default login
```

---

## 🏗️ 2. Create & Configure Your Project

Create a new project:

```bash
gcloud projects create mcp_amadeus_demo
```

Set it as the active project:

```bash
gcloud config set project mcp-amadeus-demo
```

Enable Vertex AI:

```bash
gcloud services enable aiplatform.googleapis.com
```

Set it as the billing project for API calls:

```bash
gcloud auth application-default set-quota-project mcp-amadeus-demo
```

---

## 🔐 3. Create a Service Account

This service account will manage your ADK agent.

### Option A — Using Google Cloud Console

1. Go to **IAM & Admin → Service Accounts**.
2. Click **Create Service Account**.
3. Enter:

   * **Name:** e.g. `vertex-agent`
   * **ID:** auto-generated or custom
   * **Description:** optional
4. Click **Create and Continue**.
5. Assign roles based on least privilege (learn more in IAM documentation).
6. Click **Done**.

### ✔️ Recommended Roles

(Example roles used commonly for ADK deployments)

* Vertex AI Administrator
* Storage Admin
* Service Account User

---

## 🔑 4. Create & Download a Service Account Key

1. Go to **IAM & Admin → Service Accounts**.
2. Select your service account.
3. Open the **Keys** tab.
4. Click **Add Key → Create New Key**.
5. Select **JSON**.
6. Download and **store securely**.

This key will be added to your application (e.g., Apps Script properties).

---

## 🗄️ 5. Create a Cloud Storage Bucket

Vertex AI Agent Engine uses GCS to stage deployment files.

### Option A — Cloud Console

1. Go to **Cloud Storage → Buckets**.
2. Click **Create**.
3. Use a **globally unique name**, e.g. `mcp-amadeus-bucket`.
4. Choose your region, e.g. `us-central1`.
5. Keep defaults → **Create**.

### Option B — gcloud CLI

```bash
gcloud storage buckets create gs://CLOUD_STORAGE_BUCKET_NAME \
    --project=PROJECT_ID \
    --location=PROJECT_LOCATION
```

---

## 📦 6. Generate a requirements.txt File

Include all Python dependencies:

```bash
pip freeze > requirements.txt
```

---

## 🚢 7. Deploy the Agent with ADK

Run the deployment command:

```bash
adk deploy agent_engine \
    --project=mcp-amadeus-demo \
    --region=us-central1 \
    --staging_bucket=gs://mcp-amadeus-bucket \
    --display_name="Amadeus Travel Agent" \
    --requirements_file requirements.txt \
    amadeus_test_mcp/
```

---

## 📜 8. View Deployment Logs

Use Cloud Logging to inspect agent activity:

```bash
gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
    --project=mcp-amadeus-demo \
    --limit=50 \
    --format=json
```

---

## ✅ Everything Is Ready!

You now have a complete workflow to:

* Authenticate your environment
* Configure your project
* Create service accounts and keys
* Prepare a Cloud Storage bucket
* Deploy your ADK agent
* Monitor logs in production

Feel free to request a badge-style header, architecture diagram, or auto-generated table of contents!

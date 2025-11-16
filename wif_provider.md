# Phase 2: Get Your WIF_PROVIDER
# Run these commands in Cloud Shell to link GitHub to your GCP project.

# 1. Create the Workload Identity Pool:

## Bash

gcloud iam workload-identity-pools create "github-pool" \
    --location="global" \
    --display-name="GitHub Actions Pool"

# 2. Create the Identity Provider:

## REPLACE YOUR_GITHUB_USERNAME/YOUR_REPO_NAME with your repository details.

## Bash

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --workload-identity-pool="github-pool" \
    --location="global" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="attribute.repository == '21f1000478mlops/mlops'"

# 3. Link Your Service Account:

## REPLACE YOUR_GITHUB_USERNAME/YOUR_REPO_NAME again.

## Bash

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
GSA_EMAIL="telemetry-access@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts add-iam-policy-binding "$GSA_EMAIL" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/21f1000478mlops/mlops"

# 4. Get the WIF_PROVIDER Value:

## Run this command and copy the output.

## Bash

gcloud iam workload-identity-pools providers describe "github-provider" \
    --workload-identity-pool="github-pool" \
    --location="global" \
    --format="value(name)"

## The output will look like: projects/123456/locations/global/workloadIdentityPools/github-pool/providers/github-provider

projects/277045232565/locations/global/workloadIdentityPools/github-pool/providers/github-provider -  wif value obtained from gcp
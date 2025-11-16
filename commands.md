# Enable services
gcloud services enable container.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    artifactregistry.googleapis.com \
    cloudtrace.googleapis.com

# Create GKE cluster
gcloud container clusters create iris-cluster \
  --zone=us-central1-a \
  --num-nodes=3 \
  --workload-pool=$(gcloud config get-value project).svc.id.goog \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM

# Create repository 

gcloud artifacts repositories create mlops-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for MLOps"

# Create Google Service Account (GSA):
gcloud iam service-accounts create telemetry-access \
    --display-name "Access for GKE ML service"

# Bind IAM Roles to GSA (for logging and tracing):

PROJECT_ID=$(gcloud config get-value project)
GSA_EMAIL="telemetry-access@$PROJECT_ID.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GSA_EMAIL" \
  --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GSA_EMAIL" \
  --role="roles/cloudtrace.agent"

# Also add role for pushing Docker images

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GSA_EMAIL" \
  --role="roles/artifactregistry.writer"

# Create Kubernetes Service Account (KSA):
kubectl create serviceaccount telemetry-access --namespace default

# Link GSA and KSA (Workload Identity):
PROJECT_ID=$(gcloud config get-value project)
GSA_EMAIL="telemetry-access@$PROJECT_ID.iam.gserviceaccount.com"

kubectl annotate serviceaccount telemetry-access \
  --namespace default \
  iam.gke.io/gcp-service-account=$GSA_EMAIL

gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/telemetry-access]"
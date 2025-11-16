Here are the gcloud commands to get the exact values for your GitHub secrets.

Run these in your Cloud Shell:

1. To get PROJECT_ID:

gcloud config get-value project

Example Output: dulcet-bastion-452612-v4

2. To get GSA_EMAIL:
This command constructs the email address you created in your setup scripts.


PROJECT_ID=$(gcloud config get-value project)
echo "telemetry-access@$PROJECT_ID.iam.gserviceaccount.com"

Example Output: telemetry-access@dulcet-bastion-452612-v4.iam.gserviceaccount.com

3. To get WIF_PROVIDER:
This command retrieves the full name of the Workload Identity Provider you created.

gcloud iam workload-identity-pools providers describe "github-provider" \
    --workload-identity-pool="github-pool" \
    --location="global" \
    --format="value(name)"
    
Example Output: projects/1234567890/locations/global/workloadIdentityPools/github-pool/providers/github-provider
Follow these phases in order.

#### Phase 1: One-Time Google Cloud Setup
Run the commands from your `commands.md` file (or the `wif_provider.md` file) in your Google Cloud Shell. This will:
1.  Enable all necessary APIs.
2.  Create your `iris-cluster` on GKE.
3.  Create your `mlops-repo` in Artifact Registry.
4.  Create your `telemetry-access` service account and give it the correct permissions.
5.  Link your GKE cluster to this service account using Workload Identity.

#### Phase 2: GitHub Repository Setup
1.  **Create a GitHub Repository:** Go to GitHub and create a new repository.
2.  **Add Your Files:** Upload all the files from Section 2 into your new repository, matching the folder structure.
3.  **Get `WIF_PROVIDER`:** Follow the steps in your `wif_provider.md` file. **Remember to replace `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME`** with your repository details.
4.  **Add GitHub Secrets:** In your GitHub repository, go to `Settings > Secrets and variables > Actions` and add these secrets:
    * `PROJECT_ID`: Your GCP Project ID (e.g., `dulcet-bastion-452612-v4`).
    * `GSA_EMAIL`: The full email of your service account (e.g., `telemetry-access@...`).
    * `WIF_PROVIDER`: The full value you copied from the `wif_provider.md` steps.

#### Phase 3: Run Your Assignment Scenarios

1.  **Initial Deployment (from `week-7`):**
    * Make sure you are on your `week-7` branch locally.
    * `git push origin week-7`
    * This push will **automatically trigger** the `cicd.yaml` workflow.
    * Go to the "Actions" tab in GitHub to watch it. Wait for it to complete. Your application is now live.

2.  **Run Scenario 1 (Autoscaling Test):**
    * In GitHub, go to the **"Actions"** tab.
    * Select **"Manual Stress Test"** from the left-hand workflows.
    * Click the **"Run workflow"** button.
    * Select `1000` connections and `3` max pods.
    * Click **"Run workflow"**.
    * **Observe:** Watch the pods scale to 3 in your terminal:
        `watch "kubectl get hpa,pods -l app=iris-classifier-service"`

3.  **Run Scenario 2 (Bottleneck Test):**
    * Go to **"Actions"** > **"Manual Stress Test"** > **"Run workflow"** again.
    * This time, select `2000` connections and `1` max pod.
    * Click **"Run workflow"**.
    * **Observe:** Watch the GitHub log for the `wrk` step. You will see a high number of **Socket/Read/Write errors** or **Non-2xx responses**. This confirms the bottleneck.
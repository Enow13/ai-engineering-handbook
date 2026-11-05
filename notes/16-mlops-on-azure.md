# MLOps on Azure (Azure Machine Learning) – Complete Developer Study Notes 🔷🔁

> End-to-end MLOps on Azure: data assets → tracked training jobs → pipelines → registry → managed endpoints → monitoring → GitHub Actions automation. All of it as code.

[⬅ Previous: MLOps Fundamentals](15-mlops-fundamentals.md) | [🏠 Home](../README.md) | [Next: MLOps on AWS ➡](17-mlops-on-aws.md)

## 📚 What's covered

✅ [Azure ML architecture & the workspace](#1-azure-ml-architecture)
✅ [Ways to work: Studio, CLI v2, Python SDK v2](#2-ways-to-work)
✅ [Setup: workspace & compute as code](#3-setup-workspace--compute)
✅ [Data: datastores & data assets](#4-data-datastores--data-assets)
✅ [Environments](#5-environments)
✅ [Training: command jobs + MLflow](#6-training-command-jobs--mlflow)
✅ [Hyperparameter tuning: sweep jobs](#7-hyperparameter-tuning-sweep-jobs)
✅ [AutoML](#8-automl)
✅ [Pipelines & components](#9-pipelines--components)
✅ [Model registration & registries (dev → prod)](#10-models--registries)
✅ [Deployment: managed online endpoints (blue/green) & batch endpoints](#11-deployment)
✅ [Monitoring & Responsible AI](#12-monitoring--responsible-ai)
✅ [CI/CD with GitHub Actions](#13-cicd-with-github-actions)
✅ [Security & cost](#14-security--cost)
✅ [GenAIOps on Azure (Foundry)](#15-genaiops-on-azure)
✅ [End-to-end reference architecture](#16-reference-architecture)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** Azure ML engineers, DP-100 / AI-300 candidates, and MLOps engineers on Azure.


---

## 1. Azure ML architecture

```
                         Azure Machine Learning WORKSPACE
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ Assets: Data assets · Environments · Components · Models · Jobs · Pipelines   │
 │ Compute: Compute instances · Compute clusters · Serverless · Kubernetes       │
 │ Endpoints: Managed online endpoints · Batch endpoints                          │
 │ MLflow tracking server (built in)                                              │
 └──────────────────────────────────────────────────────────────────────────────┘
   Linked resources:  Storage account (datastores) · Key Vault (secrets) ·
                      Application Insights (monitoring) · Container Registry (images)
 Shared across workspaces: Azure ML REGISTRIES (models, environments, components)
```

## 2. Ways to work

| Interface | Best for |
|---|---|
| **Azure ML Studio** (https://ml.azure.com) | Exploring, AutoML, Designer, monitoring jobs |
| **Azure CLI v2** (`az ml`, YAML files) | **CI/CD and IaC**: declarative, Git-friendly |
| **Python SDK v2** (`azure-ai-ml`) | Notebooks, programmatic workflows |
| **MLflow** | Tracking and model registry (works locally and in Azure ML) |

```bash
az extension add -n ml --upgrade -y
az configure --defaults group=rg-mlops workspace=mlw-mlops-dev
```
```python
# pip install azure-ai-ml azure-identity
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
ml_client = MLClient(DefaultAzureCredential(), "<subscription-id>", "rg-mlops", "mlw-mlops-dev")
```

## 3. Setup: workspace & compute

```bash
az group create -n rg-mlops -l eastus2
az ml workspace create -n mlw-mlops-dev -g rg-mlops
az ml compute create -n aml-cluster --type AmlCompute --size Standard_DS3_v2 \
    --min-instances 0 --max-instances 4 --idle-time-before-scale-down 120
```

| Compute | Use | Cost tip |
|---|---|---|
| Compute instance | Personal dev VM (notebooks, terminal) | Enable auto-shutdown on idle |
| Compute cluster | Training jobs, scales 0 → N | `min-instances 0` |
| Serverless compute | Jobs without managing clusters | Pay only while running |
| Kubernetes (AKS/Arc) | Your own clusters for training/inference | Shared capacity |

For production, provision with **Bicep or Terraform**, with private networking and managed identities.

## 4. Data: datastores & data assets

- **Datastore** = a connection to storage (`workspaceblobstore`, ADLS Gen2, Azure SQL...) with credentials or identity.
- **Data asset** = a **versioned** reference to data: `uri_file`, `uri_folder`, or `mltable` (tabular with a schema; required by AutoML).

```bash
az ml data create --name diabetes-data --version 1 --type uri_folder --path ./data/diabetes
```
```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
ml_client.data.create_or_update(Data(name="diabetes-data", version="1",
                                     type=AssetTypes.URI_FOLDER, path="./data/diabetes"))
```
Reference in jobs as `azureml:diabetes-data:1` or `azureml:diabetes-data@latest`.

## 5. Environments

An **environment** = Docker image + conda/pip dependencies, so every run is reproducible.
- **Curated environments** (Microsoft-maintained), e.g. `azureml://registries/azureml/environments/sklearn-1.5/labels/latest`. Check the current list, as old ones are retired.
- **Custom environments** from a conda file:

```yaml
# environment/conda.yml
name: train-env
channels: [conda-forge]
dependencies:
  - python=3.11
  - pip
  - pip: [scikit-learn, pandas, mlflow, azureml-mlflow]
```
```bash
az ml environment create --name sklearn-train --version 1 \
  --image mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu22.04:latest --conda-file environment/conda.yml
```

## 6. Training: command jobs + MLflow

**Training script** (`src/train.py`) logs with MLflow. Azure ML sets the tracking URI automatically:
```python
import argparse, glob, os
import mlflow, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

p = argparse.ArgumentParser()
p.add_argument("--training_data"); p.add_argument("--reg_rate", type=float, default=0.01)
args = p.parse_args()

mlflow.autolog()                                          # params, metrics, model logged automatically
df = pd.concat(pd.read_csv(f) for f in glob.glob(os.path.join(args.training_data, "*.csv")))
X, y = df.drop(columns=["PatientID", "Diabetic"]), df["Diabetic"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
model = LogisticRegression(C=1 / args.reg_rate, max_iter=1000).fit(X_tr, y_tr)
mlflow.log_metric("AUC", roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]))
```

**Job definition (CLI v2 YAML)** (`job.yml`):
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
code: src
command: >-
  python train.py --training_data ${{inputs.training_data}} --reg_rate ${{inputs.reg_rate}}
inputs:
  training_data:
    type: uri_folder
    path: azureml:diabetes-data@latest
  reg_rate: 0.01
environment: azureml://registries/azureml/environments/sklearn-1.5/labels/latest
compute: azureml:aml-cluster
experiment_name: diabetes-training
display_name: diabetes-train-cli
```
```bash
az ml job create -f job.yml --stream
```

**Same job with the Python SDK v2:**
```python
from azure.ai.ml import command, Input
job = command(
    code="./src",
    command="python train.py --training_data ${{inputs.training_data}} --reg_rate ${{inputs.reg_rate}}",
    inputs={"training_data": Input(type="uri_folder", path="azureml:diabetes-data@latest"), "reg_rate": 0.01},
    environment="azureml://registries/azureml/environments/sklearn-1.5/labels/latest",
    compute="aml-cluster", experiment_name="diabetes-training",
)
returned = ml_client.jobs.create_or_update(job)
print(returned.studio_url)
```

## 7. Hyperparameter tuning: sweep jobs

```python
from azure.ai.ml.sweep import Choice, Uniform

job_for_sweep = job(reg_rate=Choice([0.01, 0.1, 1.0, 10.0]))
sweep_job = job_for_sweep.sweep(
    compute="aml-cluster", sampling_algorithm="random",   # grid | random | bayesian
    primary_metric="AUC", goal="Maximize",                 # must match the mlflow.log_metric name exactly
)
sweep_job.set_limits(max_total_trials=8, max_concurrent_trials=4, timeout=3600)
# Optional early termination: from azure.ai.ml.sweep import BanditPolicy
# sweep_job.early_termination = BanditPolicy(slack_factor=0.1, evaluation_interval=1)
ml_client.jobs.create_or_update(sweep_job)
```

## 8. AutoML

AutoML tries many algorithms and preprocessing steps and ranks them by your primary metric (classification, regression, forecasting, computer vision, NLP).

```python
from azure.ai.ml import automl, Input
clf = automl.classification(
    training_data=Input(type="mltable", path="azureml:diabetes-training@latest"),
    target_column_name="Diabetic", primary_metric="accuracy", test_data_size=0.1,
    experiment_name="diabetes-automl",
)
clf.set_limits(max_trials=10, timeout_minutes=60, enable_early_termination=True)
ml_client.jobs.create_or_update(clf)       # no compute set = serverless
```

## 9. Pipelines & components

A **pipeline** chains steps (prep → train → evaluate → register), each a reusable **component** with typed inputs and outputs. Steps can be cached, run in parallel, and scheduled.

```yaml
# pipeline.yml
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
display_name: diabetes-train-pipeline
experiment_name: diabetes-pipeline
settings:
  default_compute: azureml:aml-cluster
inputs:
  raw_data:
    type: uri_folder
    path: azureml:diabetes-data@latest
jobs:
  prep:
    type: command
    code: src
    command: python prep.py --input ${{inputs.data}} --output ${{outputs.clean}}
    environment: azureml://registries/azureml/environments/sklearn-1.5/labels/latest
    inputs:
      data: ${{parent.inputs.raw_data}}
    outputs:
      clean:
        type: uri_folder
  train:
    type: command
    code: src
    command: python train.py --training_data ${{inputs.data}} --model_output ${{outputs.model}}
    environment: azureml://registries/azureml/environments/sklearn-1.5/labels/latest
    inputs:
      data: ${{parent.jobs.prep.outputs.clean}}
    outputs:
      model:
        type: mlflow_model
```
```bash
az ml job create -f pipeline.yml
az ml schedule create -f schedule.yml      # e.g. a weekly retraining schedule (cron trigger)
```
With the SDK: `@dsl.pipeline` decorates a function that wires components loaded with `load_component("prep.yml")`.

## 10. Models & registries

```bash
# Register the model produced by a job (MLflow format allows no-code deployment)
az ml model create --name diabetes-model --version 1 --type mlflow_model \
  --path azureml://jobs/<job-name>/outputs/artifacts/paths/model/
```

**Azure ML registries** share models, environments and components **across workspaces and regions**. This is the backbone of dev → test → prod promotion:

```
 DEV workspace ── train & register ──► REGISTRY (shared) ──► PROD workspace deploys the SAME artifact
```
```bash
az ml registry create -f registry.yml                     # one-time
az ml model create --name diabetes-model --version 2 --registry-name mlops-registry \
  --path azureml://jobs/<job>/outputs/artifacts/paths/model/ --type mlflow_model
```

## 11. Deployment

### Managed online endpoints (real-time)
An **endpoint** = stable URL + auth. A **deployment** = model + compute behind it. One endpoint can hold several deployments with a **traffic split** (blue/green, canary).

```yaml
# endpoint.yml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
name: diabetes-endpoint-demo
auth_mode: key            # or aml_token / aad_token
```
```yaml
# blue-deployment.yml  (MLflow model → no scoring script or environment needed)
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: blue
endpoint_name: diabetes-endpoint-demo
model: azureml:diabetes-model@latest
instance_type: Standard_DS3_v2
instance_count: 1
```
```bash
az ml online-endpoint create -f endpoint.yml
az ml online-deployment create -f blue-deployment.yml --all-traffic
az ml online-endpoint invoke -n diabetes-endpoint-demo --request-file sample-request.json

# Blue/green: add "green" with the new model, test it, then shift traffic gradually
az ml online-deployment create -f green-deployment.yml
az ml online-endpoint update -n diabetes-endpoint-demo --traffic "blue=90 green=10"
az ml online-endpoint update -n diabetes-endpoint-demo --traffic "blue=0 green=100"
az ml online-deployment delete -n blue -e diabetes-endpoint-demo --yes
```
Also: **mirror traffic** (shadow testing), autoscaling, private endpoints, and custom scoring scripts (`score.py` with `init()` and `run()`) for non-MLflow models.

### Batch endpoints
Score large datasets asynchronously on a compute cluster:
```bash
az ml batch-endpoint create -f batch-endpoint.yml
az ml batch-deployment create -f batch-deployment.yml --set-default
az ml batch-endpoint invoke -n diabetes-batch-demo --input azureml:new-patients@latest
```

## 12. Monitoring & Responsible AI

- **Azure ML model monitoring:** scheduled checks for **data drift**, **prediction drift**, **data quality** and **feature attribution drift** on production data collected from online endpoints, with alerts.
- **Application Insights / Azure Monitor:** latency, errors, requests per second, CPU/memory.
- **Responsible AI dashboard:** error analysis, fairness, model explanations (interpretability), counterfactuals and causal analysis. Generate a **Responsible AI scorecard** for stakeholders.
- **Retraining:** a drift alert → Azure Monitor action → GitHub Actions / Azure DevOps → retraining pipeline.

## 13. CI/CD with GitHub Actions

Use **OIDC federated credentials** (no stored secrets): create an Entra app registration or user-assigned managed identity, add a federated credential for your repo, and grant it a role on the workspace resource group.

```yaml
# .github/workflows/train-and-deploy.yml
name: train-and-deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  id-token: write          # needed for OIDC login
  contents: read
jobs:
  train-dev:
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az extension add -n ml -y
      - name: Run training pipeline in DEV
        run: az ml job create -f pipeline.yml -g rg-mlops-dev -w mlw-mlops-dev --stream
  deploy-prod:
    needs: train-dev
    runs-on: ubuntu-latest
    environment: prod        # add "required reviewers" on this environment = manual approval gate
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az extension add -n ml -y
      - name: Deploy new model as green and send it 10% of traffic
        run: |
          az ml online-deployment create -f green-deployment.yml -g rg-mlops-prod -w mlw-mlops-prod
          az ml online-endpoint update -n diabetes-endpoint-demo --traffic "blue=90 green=10" -g rg-mlops-prod -w mlw-mlops-prod
```
Add a CI workflow on pull requests: `flake8`/`ruff`, `pytest` for data and feature code, and validation of YAML files.

## 14. Security & cost

| Security | Cost |
|---|---|
| Managed identities for workspace, compute and endpoints | Clusters with `min-instances 0`; auto-shutdown on compute instances |
| Private endpoints + managed virtual network (workspace isolation) | Low-priority/spot VMs for training |
| Key Vault for secrets; no keys in code | Serverless compute for occasional jobs |
| RBAC: *AzureML Data Scientist*, custom roles | Right-size endpoints; autoscale; delete unused deployments |
| Azure Policy (e.g. deny public workspaces) | Budgets and alerts in Cost Management |

## 15. GenAIOps on Azure

For LLM apps, Microsoft Foundry provides the LLMOps layer:
- **Prompt and agent versioning** in Foundry projects / Git.
- **Evaluations:** built-in evaluators (groundedness, relevance, coherence, fluency, safety) run on test datasets, in CI with the `azure-ai-evaluation` SDK.
- **Tracing** with OpenTelemetry → Application Insights.
- **Content Safety** guardrails, red-teaming (AI Red Teaming Agent).
- **Deployment:** model deployments + Agent Service + API Management AI gateway.
- **Prompt flow** (in Azure ML/Foundry) for orchestrating and evaluating LLM flows.

## 16. Reference architecture

```
 GitHub repo (code, YAML, IaC)
   │ PR → CI: lint · tests · validate YAML
   │ merge → CD
   ▼
 DEV workspace: data asset → pipeline (prep → train → evaluate) → register model
   │                                  MLflow tracking · Responsible AI dashboard
   ▼
 Azure ML REGISTRY (approved model + environment)
   │ manual approval (GitHub environment reviewers)
   ▼
 PROD workspace: managed online endpoint  [blue 90% | green 10%] → 100% green
   │
   ▼
 Model monitoring (drift, quality) + App Insights ──► alert ──► retraining pipeline
```

---

## 💬 Interview questions & answers

**Q1. Walk me through MLOps on Azure end to end.**
Data lands in ADLS and is registered as versioned data assets. Training runs as tracked command or pipeline jobs on clusters with MLflow, and sweeps tune hyperparameters. The best model is registered in a shared registry. GitHub Actions with OIDC promotes it to the prod workspace and deploys it to a managed online endpoint with blue/green traffic. Model monitoring and App Insights watch for drift and health, and alerts trigger the retraining pipeline.

**Q2. Online vs batch endpoints?**
Online endpoints serve low-latency real-time requests via a REST API. Batch endpoints process large datasets asynchronously on a compute cluster and write results to storage.

**Q3. How do you do a safe model release in Azure ML?**
Deploy the new model as a second deployment (green) under the same endpoint, test it directly, optionally mirror traffic, shift 10% of traffic (canary), monitor, then move to 100% and delete blue. Rollback means shifting traffic back.

**Q4. How do you promote models from dev to prod?**
Register the approved model (and environment) in an Azure ML registry, then deploy that exact artifact from the prod workspace. No retraining in prod, with full lineage.

**Q5. Why MLflow in Azure ML?**
It's the native tracking API: workspaces act as MLflow tracking servers, so the same code works locally and in the cloud. MLflow-format models deploy without a scoring script.

**Q6. Why did my sweep job fail with "primary metric not found"?**
The `primary_metric` must exactly match the name logged with `mlflow.log_metric()` (case-sensitive), and autologged metric names differ from custom names.

**Q7. How do you authenticate GitHub Actions to Azure securely?**
OIDC federated credentials on an Entra app or managed identity, with `azure/login@v2` and `id-token: write` permission, so there are no stored client secrets. Scope roles to the resource group.

---

## ✅ Final revision checklist

- [ ] I can draw the Azure ML workspace and its linked resources.
- [ ] I can create compute and data assets with the CLI.
- [ ] I can write a command job YAML and submit it.
- [ ] I can configure a sweep job with a primary metric that matches MLflow.
- [ ] I can write a two-step pipeline YAML.
- [ ] I can register a model and explain registries for promotion.
- [ ] I can deploy to a managed online endpoint and do a blue/green traffic shift.
- [ ] I can set up GitHub Actions with OIDC and an approval gate.
- [ ] I can explain model monitoring and the Responsible AI dashboard.

## 🔗 Official docs
- Azure ML documentation: https://learn.microsoft.com/azure/machine-learning/
- Azure ML CLI v2 YAML reference: https://learn.microsoft.com/azure/machine-learning/reference-yaml-overview
- Azure ML examples: https://github.com/Azure/azureml-examples
- Microsoft MLOps v2 accelerator: https://github.com/Azure/mlops-v2

---
*My AI Engineering Study Notes* | [⬅ Previous](15-mlops-fundamentals.md) | [🏠 Home](../README.md) | [Next ➡](17-mlops-on-aws.md)

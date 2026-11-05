# MLOps on AWS (Amazon SageMaker AI) – Complete Developer Study Notes 🟧🔁

> End-to-end MLOps on AWS: S3 data → processing → training jobs → tuning → SageMaker Pipelines → Model Registry → endpoints → Model Monitor → CI/CD. All of it as code.

[⬅ Previous: MLOps on Azure](16-mlops-on-azure.md) | [🏠 Home](../README.md) | [Next: Git ➡](18-git.md)

## 📚 What's covered

✅ [SageMaker AI architecture](#1-sagemaker-ai-architecture)
✅ [Ways to work & the SageMaker Python SDK v3](#2-ways-to-work--sdk-v3)
✅ [Setup: domain, IAM role, S3](#3-setup)
✅ [Data preparation & Feature Store](#4-data-preparation--feature-store)
✅ [Training jobs (`ModelTrainer`)](#5-training-jobs)
✅ [Experiment tracking: managed MLflow](#6-experiment-tracking-managed-mlflow)
✅ [Hyperparameter tuning & Autopilot](#7-hyperparameter-tuning--autopilot)
✅ [SageMaker Pipelines](#8-sagemaker-pipelines)
✅ [Model Registry & approval](#9-model-registry--approval)
✅ [Deployment options](#10-deployment-options)
✅ [Monitoring: Model Monitor & Clarify](#11-monitoring-model-monitor--clarify)
✅ [CI/CD: SageMaker Projects, GitHub Actions, CodePipeline](#12-cicd)
✅ [Multi-account MLOps](#13-multi-account-mlops)
✅ [Security & cost](#14-security--cost)
✅ [GenAIOps on AWS (Bedrock)](#15-genaiops-on-aws)
✅ [Reference architecture](#16-reference-architecture)
✅ [Azure ML ↔ SageMaker mapping](#17-azure-ml--sagemaker-mapping)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** ML engineers on AWS, AWS ML certification candidates, and MLOps engineers.

---

## 1. SageMaker AI architecture

```
                   Amazon SageMaker Unified Studio (data + analytics + AI)
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ Amazon SageMaker AI                                                              │
 │  Studio (JupyterLab, Code Editor) · Processing jobs · Training jobs · HPO        │
 │  Pipelines · Model Registry · Managed MLflow · Feature Store · Clarify           │
 │  Endpoints (real-time, serverless, async) · Batch Transform · Model Monitor      │
 │  JumpStart (pre-trained & foundation models) · HyperPod (large-scale training)   │
 └────────────────────────────────────────────────────────────────────────────────┘
  Amazon S3 (data & artifacts) · Amazon ECR (containers) · IAM execution role ·
  CloudWatch (logs/metrics) · EventBridge (events) · KMS · VPC
```

**How SageMaker jobs work:** you point SageMaker at a **container image** (AWS-provided for scikit-learn, XGBoost, PyTorch, TensorFlow, Hugging Face, or your own image in ECR), your **code**, **data in S3** and an **instance type**. It starts instances, runs the job, writes outputs (e.g. `model.tar.gz`) to S3, and shuts everything down.

## 2. Ways to work & SDK v3

| Interface | Best for |
|---|---|
| **SageMaker Studio / Unified Studio** | Notebooks, visual pipelines, experiments |
| **SageMaker Python SDK** (`sagemaker`) | High-level Python |
| **boto3** (`sagemaker` client) / **AWS CLI** (`aws sagemaker ...`) | Low-level, stable API calls in automation |
| **CloudFormation / CDK / Terraform** | Infrastructure as code |

> ⚠️ **SageMaker Python SDK v3 (2025) changed the API.** `Estimator`, `Model`, `Predictor` and the framework-specific classes (`SKLearn`, `PyTorch`...) and `sagemaker.workflow` were **removed**. Use **`ModelTrainer`** (`sagemaker.train`) for training, **`ModelBuilder`** (`sagemaker.serve`) for deployment, and **`sagemaker.mlops.workflow`** for pipelines. Most tutorials online still show v2: pin `pip install "sagemaker<3"` to run them, or translate them to v3.

```bash
pip install sagemaker boto3          # v3.x
```

## 3. Setup

1. **SageMaker domain:** console → **Amazon SageMaker AI** → **Set up for single user** (quick setup) or **organization**. This creates the domain, a user profile, and an **execution role**.
2. **IAM execution role:** SageMaker assumes it to read and write S3, pull images from ECR, and write logs. Give it least privilege in production.
3. **S3 bucket** for data and artifacts (SageMaker's default bucket is `sagemaker-<region>-<account-id>`).

```bash
aws s3 mb s3://mlops-demo-<account-id>
aws s3 cp data/diabetes.csv s3://mlops-demo-<account-id>/data/train/diabetes.csv
```

## 4. Data preparation & Feature Store

| Tool | Use |
|---|---|
| **SageMaker Processing jobs** | Run data prep, validation or evaluation scripts on managed instances (scikit-learn, Spark containers) |
| **SageMaker Data Wrangler** (in SageMaker Canvas) | Visual data prep with 300+ transforms; export to Pipelines |
| **AWS Glue / EMR / Athena** | Big data ETL and SQL |
| **SageMaker Feature Store** | Online (low-latency) + offline (S3) feature stores; consistent features for training and inference |
| **SageMaker Ground Truth** | Data labelling |
| **SageMaker Clarify** | Pre-training **bias** detection on datasets |

## 5. Training jobs

**`train.py`** reads the SageMaker channels from environment variables and saves the model to `SM_MODEL_DIR`:
```python
import argparse, glob, os
import joblib, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

p = argparse.ArgumentParser()
p.add_argument("--reg_rate", type=float, default=0.01)
args = p.parse_args()

train_dir = os.environ.get("SM_CHANNEL_TRAIN", "data/train")      # S3 channel mounted here
model_dir = os.environ.get("SM_MODEL_DIR", "model")               # anything saved here → model.tar.gz in S3
df = pd.concat(pd.read_csv(f) for f in glob.glob(os.path.join(train_dir, "*.csv")))
X, y = df.drop(columns=["PatientID", "Diabetic"]), df["Diabetic"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0)
model = LogisticRegression(C=1 / args.reg_rate, max_iter=1000).fit(X_tr, y_tr)
print(f"validation:auc={roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]):.4f}")  # parsed by metric regex
os.makedirs(model_dir, exist_ok=True)
joblib.dump(model, os.path.join(model_dir, "model.joblib"))
```

**Launch with SDK v3 `ModelTrainer`:**
```python
from sagemaker.core import image_uris
from sagemaker.train import ModelTrainer
from sagemaker.train.configs import Compute, InputData, SourceCode

image = image_uris.retrieve(framework="sklearn", region="us-east-1", version="1.2-1",
                            py_version="py3", instance_type="ml.m5.large")
trainer = ModelTrainer(
    training_image=image,
    role="arn:aws:iam::<account-id>:role/<SageMakerExecutionRole>",
    source_code=SourceCode(source_dir="src", entry_script="train.py", requirements="requirements.txt"),
    compute=Compute(instance_type="ml.m5.large", instance_count=1),   # enable_managed_spot_training=True saves cost
    hyperparameters={"reg_rate": 0.01},
    base_job_name="diabetes-train",
)
trainer.train(input_data_config=[InputData(channel_name="train",
                                           data_source="s3://mlops-demo-<account-id>/data/train/")])
```

Other training options: **local mode** (test the container on your machine first), **managed spot training** (up to ~90% cheaper; use checkpoints), **distributed training** (data/model parallel libraries), **HyperPod** (resilient clusters for foundation-model training), and **JumpStart** fine-tuning of pre-trained models.

## 6. Experiment tracking: managed MLflow

SageMaker AI offers **managed MLflow tracking servers** (create one in Studio → MLflow). Use the standard MLflow API with the tracking server ARN:
```python
# pip install mlflow sagemaker-mlflow
import mlflow
mlflow.set_tracking_uri("arn:aws:sagemaker:us-east-1:<account-id>:mlflow-tracking-server/<name>")
mlflow.set_experiment("diabetes")
with mlflow.start_run():
    mlflow.log_param("reg_rate", 0.01)
    mlflow.log_metric("auc", 0.85)
```
MLflow-registered models can be synced to the **SageMaker Model Registry**.

## 7. Hyperparameter tuning & Autopilot

- **Automatic Model Tuning (HPO):** runs many training jobs in parallel. Strategies: **Bayesian**, random, grid, **Hyperband** (early stopping). You define ranges (continuous, integer, categorical) and an objective metric parsed from logs, e.g. `validation:auc`.
- **SageMaker Autopilot** (via **SageMaker Canvas**): AutoML for tabular data, time series, text and images. It explores algorithms and preprocessing and produces explainability reports.
- In SDK v3 tuning is configured with the training config; in pipelines use `TuningStep`. With boto3: `create_hyper_parameter_tuning_job`.

## 8. SageMaker Pipelines

The **native ML workflow orchestrator**: a DAG of steps, defined in Python, executed serverlessly, with lineage tracking and caching.

| Step | Purpose |
|---|---|
| `ProcessingStep` | Data prep, validation, evaluation |
| `TrainingStep` | Train a model |
| `TuningStep` | Hyperparameter tuning |
| `ConditionStep` | Branch (e.g. register only if AUC ≥ 0.80) |
| `ModelStep` | Create or register a model |
| `QualityCheckStep` / `ClarifyCheckStep` | Data quality, bias and explainability baselines |
| `TransformStep`, `LambdaStep`, `CallbackStep`, `FailStep`, `EMRStep`, `NotebookJobStep` | Batch scoring, custom logic, external systems, explicit failure |

**Typical training pipeline:**
```
 ProcessingStep (prep + split)
        │
        ▼
 TrainingStep ──► ProcessingStep (evaluate → evaluation.json)
                          │
                          ▼
                 ConditionStep: AUC ≥ 0.80 ?
                   ├─ yes → ModelStep: register in Model Registry (status: PendingManualApproval)
                   └─ no  → FailStep ("model below threshold")
```
In SDK v3 these come from `sagemaker.mlops.workflow` (`Pipeline`, `ProcessingStep`, `TrainingStep`, `ConditionStep`, `ModelStep`...). You build steps from your trainer/processor objects, then `pipeline.upsert(role_arn=...)` and `pipeline.start()`. Pipelines can also be scheduled (`PipelineSchedule`) or triggered by **EventBridge** (e.g. new data in S3).

## 9. Model Registry & approval

- **Model package groups** = one group per use case; each registered version is a **model package** with metrics, lineage and an **approval status**: `PendingManualApproval` → `Approved` / `Rejected`.
- Approval can be manual (Studio or API) and drives deployment: an **EventBridge rule** on "model package approved" triggers the deployment pipeline.

```bash
aws sagemaker list-model-packages --model-package-group-name diabetes-models
aws sagemaker update-model-package --model-package-arn <arn> --model-approval-status Approved
```

## 10. Deployment options

| Option | Use | Notes |
|---|---|---|
| **Real-time endpoint** | Low latency, steady traffic | Instances always on; autoscaling |
| **Serverless inference** | Spiky or low traffic | Scales to zero; cold starts |
| **Asynchronous inference** | Large payloads, long processing (up to an hour) | Queue-based; can scale to zero |
| **Batch Transform** | Score datasets offline | No persistent endpoint |
| **Multi-model / multi-container endpoints, inference components** | Many models on shared infrastructure | Cost-efficient hosting |
| **Edge** | Devices | IoT Greengrass |

**Deploy with SDK v3 `ModelBuilder`:**
```python
from sagemaker.serve import ModelBuilder
builder = ModelBuilder(model=trainer,                       # a trained ModelTrainer, S3 model data, or a JumpStart id
                       role_arn="arn:aws:iam::<account-id>:role/<SageMakerExecutionRole>",
                       instance_type="ml.m5.large")
endpoint = builder.build()                                    # see the v3 examples for deploy/invoke on your version
```

**Safe deployments (built-in deployment guardrails):** **blue/green** with **all-at-once, canary or linear** traffic shifting, automatic **rollback on CloudWatch alarms**, and **shadow testing** (send a copy of production traffic to a new variant and compare). **Production variants** split traffic between models for A/B tests.

```bash
# Invoke a deployed endpoint (stable API, works whatever SDK built it)
aws sagemaker-runtime invoke-endpoint --endpoint-name diabetes-endpoint \
  --content-type text/csv --body "2,180,74,24,21,23.9,1.48,22" out.json
```

## 11. Monitoring: Model Monitor & Clarify

**SageMaker Model Monitor** compares production traffic (via **data capture** on the endpoint) against a **baseline** from training data, on a schedule:

| Monitor type | Detects |
|---|---|
| **Data quality** | Schema violations, missing values, distribution drift |
| **Model quality** | Accuracy/AUC drop (needs ground-truth labels uploaded later) |
| **Bias drift** (Clarify) | Fairness metrics changing in production |
| **Feature attribution drift** (Clarify) | Feature importance (SHAP) changing |

Violations are published to **CloudWatch** → alarm → **EventBridge** → trigger the retraining pipeline.
**SageMaker Clarify** also produces **explainability reports** (SHAP) and **bias reports** before deployment.

## 12. CI/CD

| Option | How |
|---|---|
| **SageMaker Projects** | MLOps templates that create repos and CI/CD (model build + model deploy pipelines) with Service Catalog |
| **GitHub Actions** | OIDC role assumption (`aws-actions/configure-aws-credentials`) → run tests → upsert/start the pipeline |
| **AWS CodePipeline + CodeBuild** | AWS-native CI/CD; deploy with CloudFormation to staging → manual approval → prod |

**GitHub Actions with OIDC (no stored AWS keys):**
```yaml
# .github/workflows/model-build.yml
name: model-build
on:
  push:
    branches: [main]
permissions:
  id-token: write
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::<account-id>:role/github-actions-mlops
          aws-region: us-east-1
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt && pytest -q
      - name: Create/update and start the SageMaker pipeline
        run: python pipelines/run_pipeline.py      # builds steps, pipeline.upsert(...), pipeline.start()
```
**Model deploy** runs separately: triggered when a model is **approved** in the registry → deploy to **staging** → automated tests → **manual approval** → **prod** (CloudFormation/CDK).

## 13. Multi-account MLOps

AWS best practice separates accounts with **AWS Organizations**:
```
 Data account (lake) ─► Dev/Experimentation account ─► Shared services (registry, ECR, CI/CD tooling)
                                                         │ cross-account model sharing (RAM / resource policies)
                                                         ├─► Staging account (test endpoints)
                                                         └─► Production account (prod endpoints)
```
This gives blast-radius isolation, separate permissions and clear cost allocation.

## 14. Security & cost

| Security | Cost |
|---|---|
| Least-privilege **execution roles**; no access keys | **Managed spot training** with checkpoints |
| **VPC mode** for jobs and endpoints; **VPC endpoints** for S3/SageMaker | Serverless / async inference that scales to zero |
| **KMS** encryption for volumes, S3 and endpoints | Right-size instances; **Inference Recommender** load tests |
| **Network isolation** for training containers | Multi-model endpoints / inference components |
| CloudTrail auditing; SageMaker Role Manager | Stop idle Studio apps (lifecycle configs); **SageMaker Savings Plans** |

## 15. GenAIOps on AWS

- **Bedrock** for models; **prompt management** and versioning; **Bedrock evaluations** (LLM-as-a-judge, RAG evaluation) in CI.
- **Guardrails** as code (CloudFormation/CDK).
- **Fine-tuning / distillation** in Bedrock, or SageMaker AI for open models (JumpStart, HyperPod).
- **Agents:** Bedrock AgentCore for runtime, observability and evaluation.
- **Observability:** CloudWatch GenAI observability, AgentCore traces, MLflow GenAI tracing.

## 16. Reference architecture

```
 Git repo ──► GitHub Actions / CodePipeline (CI: tests)
                 │
                 ▼
 SageMaker Pipeline (DEV): Processing → Training → Evaluate → Condition → Register (PendingManualApproval)
                 │                        Managed MLflow · Clarify bias/explainability
                 ▼
 Model Registry ──(Approved)──► EventBridge ──► Deploy pipeline
                                                  ├─► Staging endpoint → tests
                                                  └─► manual approval → Prod endpoint (blue/green canary,
                                                                          auto-rollback on alarms)
 Prod endpoint data capture ──► Model Monitor (data/model quality, bias, attribution drift)
                                   └─► CloudWatch alarm ──► EventBridge ──► retraining pipeline
```

## 17. Azure ML ↔ SageMaker mapping

| Azure Machine Learning | Amazon SageMaker AI |
|---|---|
| Workspace | Domain (+ account/region) |
| Compute instance | Studio space / notebook instance |
| Compute cluster / serverless | Training job instances (ephemeral) |
| Data asset / datastore | S3 URIs / Feature Store |
| Environment | Container image (ECR) + requirements |
| Command job | Training job (`ModelTrainer`) |
| Sweep job | Automatic Model Tuning (HPO) |
| AutoML | Autopilot (SageMaker Canvas) |
| Pipeline | SageMaker Pipelines |
| MLflow (built in) | Managed MLflow |
| Model registry / registries | Model Registry (model package groups) |
| Managed online endpoint | Real-time endpoint |
| Batch endpoint | Batch Transform |
| Model monitoring | Model Monitor |
| Responsible AI dashboard | SageMaker Clarify |
| GitHub Actions / Azure DevOps | GitHub Actions / CodePipeline / SageMaker Projects |

---

## 💬 Interview questions & answers

**Q1. Walk me through MLOps on AWS end to end.**
Data in S3 (Glue/Processing for prep, Feature Store for features). A SageMaker Pipeline runs processing → training → evaluation → a condition → registers the model as PendingManualApproval. On approval, EventBridge triggers deployment to staging, tests, manual approval, then a production endpoint with blue/green canary and auto-rollback. Model Monitor watches data capture for drift, and CloudWatch alarms trigger retraining. CI/CD runs in GitHub Actions (OIDC) or CodePipeline, across separate accounts.

**Q2. Real-time vs serverless vs async vs batch inference?**
Real-time: always-on, low latency. Serverless: scales to zero for spiky or low traffic, with cold starts. Async: queued, large payloads or long processing, can scale to zero. Batch Transform: offline scoring of whole datasets, no endpoint.

**Q3. How does SageMaker training work under the hood?**
SageMaker launches instances with a container image, copies your code and the S3 data channels in (`SM_CHANNEL_*`), runs the entry script, uploads everything in `SM_MODEL_DIR` to S3 as `model.tar.gz`, streams logs to CloudWatch, then terminates the instances.

**Q4. How do you gate model promotion?**
An evaluation step writes metrics, and a ConditionStep only registers the model if it beats the threshold or the current champion. Registration is PendingManualApproval, and approval triggers deployment via EventBridge. Production also uses deployment guardrails with alarm-based rollback.

**Q5. How does Model Monitor detect drift?**
It baselines statistics and constraints from training data, captures production requests and responses, runs scheduled monitoring jobs comparing them to the baseline, and emits violations and CloudWatch metrics.

**Q6. What changed in SageMaker Python SDK v3?**
Estimator, Model, Predictor and the framework-specific classes were removed. Training uses `ModelTrainer`, deployment uses `ModelBuilder`, and pipelines live in `sagemaker.mlops.workflow`. v2 code needs `sagemaker<3` or migration.

**Q7. How do you cut SageMaker costs?**
Managed spot training with checkpoints, serverless/async inference for intermittent traffic, multi-model endpoints, right-sizing with Inference Recommender, auto-stopping idle Studio apps, Savings Plans, and deleting unused endpoints.

---

## ✅ Final revision checklist

- [ ] I can explain how a SageMaker training job runs (image, code, S3 channels, model dir).
- [ ] I can write a `train.py` using `SM_CHANNEL_*` and `SM_MODEL_DIR`.
- [ ] I know the SDK v3 classes: `ModelTrainer`, `ModelBuilder`, `sagemaker.mlops.workflow`.
- [ ] I can draw a SageMaker Pipeline with a condition-gated registration.
- [ ] I can explain Model Registry approval and EventBridge-triggered deployment.
- [ ] I can compare the four inference options and the deployment guardrails.
- [ ] I can list the four Model Monitor types.
- [ ] I can set up GitHub Actions with OIDC for AWS.
- [ ] I can map Azure ML concepts to SageMaker.

## 🔗 Official docs
- Amazon SageMaker AI developer guide: https://docs.aws.amazon.com/sagemaker/latest/dg/
- SageMaker Python SDK (v3): https://sagemaker.readthedocs.io/
- SageMaker v3 examples: https://github.com/aws/sagemaker-python-sdk/tree/master/v3-examples
- AWS MLOps whitepaper / guidance: https://docs.aws.amazon.com/wellarchitected/latest/machine-learning-lens/

---
*My AI Engineering Study Notes* | [⬅ Previous](16-mlops-on-azure.md) | [🏠 Home](../README.md) | [Next ➡](18-git.md)

# MLOps & LLMOps Fundamentals – Complete Developer Study Notes 🔁⚙️

> Most ML models never reach production, and many that do quietly degrade. MLOps is the engineering discipline that fixes both: repeatable training, safe releases, and constant monitoring.

[⬅ Previous: AWS AI Services](14-aws-ai-services.md) | [🏠 Home](../README.md) | [Next: MLOps on Azure ➡](16-mlops-on-azure.md)

## 📚 What's covered

✅ [What MLOps is & why it matters](#1-what-mlops-is)
✅ [The ML lifecycle](#2-the-ml-lifecycle)
✅ [MLOps maturity levels](#3-mlops-maturity-levels)
✅ [Core building blocks](#4-core-building-blocks)
✅ [Experiment tracking with MLflow](#5-experiment-tracking-with-mlflow)
✅ [CI/CD/CT for ML](#6-cicdct-for-ml)
✅ [Environments: dev → test → prod](#7-environments)
✅ [Deployment patterns](#8-deployment-patterns)
✅ [Monitoring & retraining](#9-monitoring--retraining)
✅ [Docker & Kubernetes essentials](#10-docker--kubernetes-essentials)
✅ [LLMOps: what changes for GenAI](#11-llmops)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** ML engineers, MLOps/platform engineers, and DevOps engineers moving into AI.

---

## 1. What MLOps is

**MLOps** = DevOps principles applied to machine learning: automate and standardise how models are **built, tested, deployed, monitored and retrained**, with collaboration between data scientists, ML engineers and operations.

**Why ML is harder than normal software:** ML systems depend on **code + data + model**. Any of the three can change, and models degrade silently when the world changes (drift), even if the code never does.

## 2. The ML lifecycle

```
 ┌── Business problem & metrics
 │
 ▼
 Data ingestion → Validation → Feature engineering ─┐
                                                   ▼
          ┌──────────── Experimentation (notebooks, tracking) ───────────┐
          ▼                                                              │
 Training pipeline → Evaluation → Model registry → Approval → Deployment │
                                                       │                 │
                                                       ▼                 │
                                   Monitoring (data drift, performance,  │
                                   latency, cost) ──► Retraining trigger ┘
```

## 3. MLOps maturity levels

| Level | Description |
|---|---|
| **0 – Manual** | Notebooks, manual training and deployment, no tracking. Hard to reproduce |
| **1 – ML pipeline automation** | Automated training pipelines, experiment tracking, model registry; continuous training on new data |
| **2 – CI/CD pipeline automation** | Pipelines themselves are tested and deployed via CI/CD; automated promotion through environments, monitoring and retraining triggers |

(Google's and Microsoft's maturity models differ slightly, but they follow the same progression.)

## 4. Core building blocks

| Block | Purpose | Examples |
|---|---|---|
| **Version control** | Code, configs, pipeline definitions | Git, GitHub, Azure Repos |
| **Data versioning** | Reproduce training data | Azure ML data assets, DVC, S3 versioning, Delta Lake |
| **Experiment tracking** | Params, metrics, artifacts per run | **MLflow**, Azure ML jobs, SageMaker Experiments |
| **Feature store** | Reuse consistent features for training and serving | Azure ML feature store, SageMaker Feature Store, Feast |
| **Pipelines / orchestration** | Repeatable multi-step workflows | Azure ML pipelines, SageMaker Pipelines, Kubeflow, Airflow |
| **Environments** | Reproducible dependencies | Docker, conda, Azure ML environments |
| **Model registry** | Versioned, approved models with lineage | MLflow registry, Azure ML registries, SageMaker Model Registry |
| **Serving** | Real-time or batch inference | Managed endpoints, KServe, Seldon, BentoML |
| **Monitoring** | Drift, quality, latency, cost | Azure ML model monitoring, SageMaker Model Monitor, Evidently |
| **IaC** | Reproducible infrastructure | Terraform, Bicep, CloudFormation, CDK |
| **CI/CD** | Automated test and release | GitHub Actions, Azure DevOps, Jenkins, CodePipeline |

## 5. Experiment tracking with MLflow

**MLflow** (open source) is the standard for tracking. Both Azure ML (natively) and SageMaker AI (managed MLflow) support it.

```python
# pip install mlflow scikit-learn
import mlflow
from sklearn.datasets import load_diabetes
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

X, y = load_diabetes(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, random_state=0)

mlflow.set_experiment("diabetes-ridge")
for alpha in [0.1, 1.0, 10.0]:
    with mlflow.start_run():
        model = Ridge(alpha=alpha).fit(X_tr, y_tr)
        rmse = mean_squared_error(y_te, model.predict(X_te)) ** 0.5
        mlflow.log_param("alpha", alpha)                 # what you tried
        mlflow.log_metric("rmse", rmse)                  # how it did
        mlflow.sklearn.log_model(model, name="model")    # the artifact (older MLflow: artifact_path="model")
# View locally: mlflow ui  → http://127.0.0.1:5000
```

`mlflow.autolog()` logs parameters, metrics and models automatically for popular libraries.

## 6. CI/CD/CT for ML

| Practice | In ML |
|---|---|
| **CI (Continuous Integration)** | On every pull request: lint, unit-test code (feature functions, data validation), test that the pipeline definition builds, small "smoke" training run |
| **CD (Continuous Delivery/Deployment)** | Promote a **registered, approved** model through test → staging → prod; infrastructure as code |
| **CT (Continuous Training)** | Retrain automatically on a schedule, on new data, or when drift is detected |

**Quality gates before promotion:** metric above a threshold *and* no worse than the current production model ("champion vs challenger"), fairness and bias checks, latency test, security scan, human approval for production.

**Example GitHub Actions flow:**
```
PR opened ─► CI: lint + pytest + validate pipeline YAML
merge to main ─► CD-dev: run training pipeline in DEV workspace → register model
manual approval ─► CD-prod: deploy model to PROD endpoint (blue/green) → smoke test → shift traffic
schedule / drift alert ─► CT: retrain → evaluate → register → (approval) → deploy
```

## 7. Environments

| Environment | Purpose | Data |
|---|---|---|
| **Dev** | Experimentation, building pipelines | Sample or anonymised data |
| **Test / Staging** | Integration tests, performance tests, validation | Production-like |
| **Prod** | Serves real users | Real data, strict access |

Use **separate workspaces/accounts** per environment, **promote artifacts** (models, images) instead of retraining in prod, and share models through a **registry** (Azure ML registries, SageMaker Model Registry with cross-account access).

## 8. Deployment patterns

| Pattern | Description | Use |
|---|---|---|
| **Real-time (online)** | Low-latency API per request | Fraud check at checkout |
| **Batch** | Score large datasets on a schedule | Nightly churn scores |
| **Streaming** | Score events as they arrive | IoT anomaly detection |
| **Edge** | Model runs on device | Mobile, factory cameras |
| **Serverless inference** | Scales to zero; pay per request | Spiky, low traffic |

**Release strategies:**
| Strategy | How | Benefit |
|---|---|---|
| **Blue/green** | Deploy new (green) next to old (blue), then switch traffic | Instant rollback |
| **Canary** | Send 5–10% of traffic to the new model first | Limit blast radius |
| **Shadow** | New model receives a copy of traffic; its answers aren't used | Test on real traffic safely |
| **A/B test** | Split users and compare business metrics | Measure real impact |

## 9. Monitoring & retraining

| Monitor | Examples |
|---|---|
| **Data drift** | Input distributions change (PSI, KS test, Jensen–Shannon) |
| **Prediction drift** | Output distribution changes |
| **Model performance** | Accuracy or F1 once ground-truth labels arrive (may be delayed) |
| **Data quality** | Missing values, schema changes, out-of-range values |
| **Operational** | Latency (p95), errors, throughput, CPU/GPU, cost |
| **Fairness** | Performance across groups over time |

**Retraining triggers:** schedule (weekly), data volume (N new labelled rows), drift threshold breached, or a performance drop. Always **evaluate before replacing** the production model.

## 10. Docker & Kubernetes essentials

```dockerfile
# Dockerfile for a FastAPI model server
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
COPY model/ model/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

| Kubernetes object | Role |
|---|---|
| **Pod** | Runs one or more containers |
| **Deployment** | Keeps N replicas running; rolling updates |
| **Service** | Stable network address for pods |
| **Ingress** | HTTP routing from outside |
| **HPA** | Autoscale on CPU/memory/custom metrics |
| **ConfigMap / Secret** | Configuration and secrets |
| **Node pool (GPU)** | Nodes with GPUs for inference |

Managed: **AKS** (Azure), **EKS** (AWS). ML on Kubernetes: **KServe**, **Kubeflow**, **Ray**, and Azure ML Kubernetes compute.

## 11. LLMOps

LLMOps (or GenAIOps) = MLOps for LLM applications. What changes:

| MLOps | LLMOps |
|---|---|
| Train your own model | Mostly **use** foundation models (+ sometimes fine-tune) |
| Version code, data, model | Also version **prompts**, RAG index/chunking config, tool definitions, model versions |
| Metrics: accuracy, F1, RMSE | **Groundedness, relevance, faithfulness, toxicity, refusal rate**, LLM-as-a-judge |
| Training cost | **Token cost per request**, latency |
| Data drift | Also **query drift**, new document types, prompt injection attempts |
| Model registry | Prompt registry + evaluation datasets + model routing |

**LLMOps pipeline:** change prompt/RAG config → run the **evaluation set** in CI (quality + safety) → compare with production → deploy (canary) → **trace** every call (inputs, retrieved chunks, tool calls, tokens) → collect user feedback → improve.

Tools: Microsoft Foundry (evaluations, tracing), Amazon Bedrock (evaluations, guardrails), LangSmith, Langfuse, MLflow (GenAI tracing and evaluation), promptfoo.

---

## 💬 Interview questions & answers

**Q1. What is MLOps and why is it needed?**
Practices and tools to reliably build, deploy, monitor and retrain ML models. It's needed because ML depends on code, data and model, all of which change, and models silently degrade, so you need reproducibility, automation and monitoring.

**Q2. CI vs CD vs CT in ML?**
CI tests code and pipeline definitions on every change. CD promotes approved models and infrastructure through environments. CT automatically retrains models on new data or drift.

**Q3. How do you decide whether a new model should replace production?**
Champion/challenger: evaluate both on the same recent holdout data and business metrics, check fairness, latency and cost, then use canary or shadow deployment before a full rollout, with human approval for production.

**Q4. Blue/green vs canary?**
Blue/green runs two full versions and switches traffic all at once (instant rollback). Canary shifts a small percentage first and increases gradually while monitoring.

**Q5. How do you monitor a model when labels arrive weeks later?**
Monitor proxies in the meantime: data drift, prediction drift, data quality and business KPIs. Then compute real performance when labels arrive and backfill.

**Q6. What's different about LLMOps?**
You version prompts and RAG configurations as well as models, evaluate with GenAI metrics (groundedness, relevance, safety) using LLM judges and human review, trace every call, and manage token cost and latency.

**Q7. Why use a model registry?**
A single source of truth for versioned models with metadata, lineage (which data and code produced it), stage or approval status, and controlled promotion across environments.

---

## ✅ Final revision checklist

- [ ] I can draw the ML lifecycle and explain the three maturity levels.
- [ ] I can list the core MLOps building blocks with an example tool each.
- [ ] I can track experiments with MLflow.
- [ ] I can explain CI, CD and CT and list promotion quality gates.
- [ ] I can compare real-time, batch, streaming and serverless deployment.
- [ ] I can explain blue/green, canary, shadow and A/B.
- [ ] I can list what to monitor and the retraining triggers.
- [ ] I can explain how LLMOps differs from MLOps.

## 🔗 Official docs
- MLflow: https://mlflow.org/docs/latest/
- Microsoft MLOps guidance: https://learn.microsoft.com/azure/machine-learning/concept-model-management-and-deployment
- Google, "MLOps: Continuous delivery and automation pipelines": https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning

---
*My AI Engineering Study Notes* | [⬅ Previous](14-aws-ai-services.md) | [🏠 Home](../README.md) | [Next ➡](16-mlops-on-azure.md)

# Training Data – Complete Developer Study Notes 🗂️🧪

> Models are a reflection of their data. The fastest way to a better model is usually better data, not a better algorithm.

[⬅ Previous: Deep Learning](03-deep-learning-and-transformers.md) | [🏠 Home](../README.md) | [Next: GenAI & Prompting ➡](05-generative-ai-and-prompt-engineering.md)

## 📚 What's covered

✅ [What training data is & the data lifecycle](#1-what-training-data-is)
✅ [Data types & formats](#2-data-types--formats)
✅ [Data quality dimensions](#3-data-quality-dimensions)
✅ [Collecting & labelling data](#4-collecting--labelling-data)
✅ [Cleaning & preprocessing checklist](#5-cleaning--preprocessing-checklist)
✅ [Splitting, leakage & imbalance](#6-splitting-leakage--imbalance)
✅ [Training data for LLMs: pre-training, SFT, preference data](#7-training-data-for-llms)
✅ [Fine-tuning dataset formats (JSONL)](#8-fine-tuning-dataset-formats)
✅ [Synthetic data & augmentation](#9-synthetic-data--augmentation)
✅ [Versioning, lineage & governance](#10-versioning-lineage--governance)
✅ [Data drift in production](#11-data-drift)
✅ [Cloud tools for training data (Azure & AWS)](#12-cloud-tools-for-training-data)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** ML engineers, data scientists, GenAI developers fine-tuning models, and MLOps engineers.

---

## 1. What training data is

**Training data** = the examples a model learns from. For supervised learning, each example has **features** (inputs) and a **label** (the correct answer).

```
Collect ─► Label ─► Clean ─► Explore (EDA) ─► Split ─► Version ─► Train ─► Monitor ─► Refresh
```

## 2. Data types & formats

| Type | Examples | Typical formats |
|---|---|---|
| **Structured / tabular** | Transactions, sensor readings, CRM data | CSV, Parquet, SQL tables, Delta |
| **Unstructured text** | Emails, tickets, documents, chat logs | TXT, PDF, DOCX, HTML, JSON |
| **Images / video** | X-rays, product photos, CCTV | JPG, PNG, MP4 (+ annotation files: COCO JSON, Pascal VOC XML) |
| **Audio** | Calls, voice commands | WAV, MP3, FLAC (+ transcripts) |
| **Time series** | Stock prices, IoT telemetry | CSV, Parquet, time-series DBs |
| **LLM fine-tuning** | Prompt → response pairs, conversations | **JSONL** (one JSON object per line) |

💡 **Parquet** is preferred over CSV for big tabular data: columnar, compressed, keeps data types, and is fast to query.

## 3. Data quality dimensions

| Dimension | Question | Example problem |
|---|---|---|
| **Accuracy** | Are values correct? | Wrong labels, typos |
| **Completeness** | Is anything missing? | Empty income field |
| **Consistency** | Same thing, same format? | "USA", "U.S.", "United States" |
| **Timeliness** | Is it recent enough? | 2019 data for 2026 behaviour |
| **Validity** | Within allowed rules/ranges? | Age = -5 |
| **Uniqueness** | Duplicates? | Same customer twice (inflates results; leaks across splits) |
| **Representativeness** | Does it match production users? | Only one region or demographic |

## 4. Collecting & labelling data

**Sources:** internal databases, logs, APIs, public datasets (Kaggle, Hugging Face Datasets, UCI), data vendors, user feedback, synthetic generation.

**Labelling approaches:**

| Approach | Pros | Cons |
|---|---|---|
| In-house experts | High quality (medical, legal) | Expensive, slow |
| Crowdsourcing | Fast, scalable | Needs quality control |
| Programmatic / weak labelling | Rules label lots of data quickly | Noisy |
| Model-assisted (pre-label, human corrects) | Fast + accurate | Risk of copying the model's bias |
| LLM-as-labeller | Very fast for text | Must be validated against a human-labelled sample |
| Active learning | Humans label only the examples the model is unsure about | Needs a feedback loop |

**Quality controls:** clear labelling guidelines with examples, multiple labellers per item, **inter-annotator agreement** (Cohen's kappa), gold-standard test questions, regular audits.

## 5. Cleaning & preprocessing checklist

- [ ] Remove exact and near **duplicates**
- [ ] Handle **missing values** (impute or flag; don't silently drop half the data)
- [ ] Fix **types** (dates as dates, numbers as numbers)
- [ ] Standardise **categories** and units
- [ ] Detect and treat **outliers** (investigate before deleting)
- [ ] Remove or mask **PII** (names, emails, IDs) unless needed and allowed
- [ ] Check **label quality** on a sample
- [ ] For text: normalise whitespace and encoding, strip boilerplate, de-duplicate, detect language
- [ ] Document every step (so it's reproducible)

```python
import pandas as pd

df = pd.read_csv("customers.csv")
print(df.shape, df.isna().mean().round(3).to_dict())     # size and % missing per column
df = df.drop_duplicates()
df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
df["country"] = df["country"].str.strip().str.upper().replace({"U.S.": "USA", "UNITED STATES": "USA"})
df = df[df["age"].between(18, 100)]                      # validity rule
print(df["churned"].value_counts(normalize=True))        # class balance
```

## 6. Splitting, leakage & imbalance

- **Split first, then fit any preprocessing on the training split only.**
- **Group-aware splits:** keep all rows of one customer or patient in the **same** split (`GroupKFold`), otherwise the model memorises people.
- **Time-based splits** for anything that changes over time.
- **Leakage red flags:** a feature that's "too good", features created after the outcome, duplicates across splits.
- **Imbalance:** stratify splits, use class weights or resampling, and evaluate with F1 or PR-AUC.

## 7. Training data for LLMs

| Stage | Data | Size | Goal |
|---|---|---|---|
| **Pre-training** | Web text, books, code, papers (filtered and de-duplicated) | Trillions of tokens | Learn language and knowledge (next-token prediction) |
| **Supervised fine-tuning (SFT)** | High-quality instruction → response pairs | Thousands to millions | Follow instructions, format, tone |
| **Preference data** (RLHF/DPO) | Prompt + preferred vs rejected answer | Thousands to millions | Helpful, harmless, honest behaviour |
| **Your fine-tuning** | Your domain examples | Hundreds to thousands of **high-quality** examples | Your task, style or format |
| **RAG data** (not training!) | Your documents, chunked and embedded | Any | Knowledge at query time |

💡 For fine-tuning, **quality beats quantity**: 500 excellent, diverse, correct examples often beat 50,000 noisy ones.

## 8. Fine-tuning dataset formats

Most providers (Azure OpenAI in Foundry, Amazon Bedrock, OpenAI, Hugging Face) use **JSONL**, one example per line.

**Chat format** (most common):
```json
{"messages": [{"role": "system", "content": "You are Contoso's IT assistant."}, {"role": "user", "content": "How long must my laptop password be?"}, {"role": "assistant", "content": "At least 12 characters, with uppercase, lowercase, numbers and special characters (IT Security Policy)."}]}
{"messages": [{"role": "system", "content": "You are Contoso's IT assistant."}, {"role": "user", "content": "Which VPN do we use?"}, {"role": "assistant", "content": "Cisco AnyConnect. Connect before starting work (IT Security Policy)."}]}
```

**Prompt–completion format** (some services, for example Bedrock model customisation):
```json
{"prompt": "Classify the ticket: 'My laptop won't boot'", "completion": "hardware"}
```

**Preference (DPO) format:**
```json
{"prompt": "Explain RAG briefly.", "chosen": "RAG retrieves relevant documents and gives them to the model so answers are grounded...", "rejected": "RAG is a type of database."}
```

**Validate before uploading:**
```python
import json
with open("train.jsonl", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        row = json.loads(line)                                   # fails on invalid JSON
        roles = [m["role"] for m in row["messages"]]
        assert roles[-1] == "assistant", f"line {i}: last message must be the assistant"
print("train.jsonl is valid")
```

## 9. Synthetic data & augmentation

| Technique | Use |
|---|---|
| **LLM-generated examples** | Bootstrap Q&A pairs, edge cases, rare classes (review a sample by hand!) |
| **Paraphrasing / back-translation** | More varied text |
| **Image augmentation** | Flips, crops, colour shifts, noise |
| **SMOTE** | Synthetic minority-class rows for tabular data |
| **Privacy-preserving synthetic data** | Share realistic data without real PII |

⚠️ Risks: synthetic data can copy the generator's mistakes and biases, and training models on model output repeatedly can cause **model collapse**. Always keep a **real, human-checked test set**.

## 10. Versioning, lineage & governance

- **Version data like code:** Azure ML **data assets** (versioned), SageMaker AI **Feature Store** / S3 object versioning, **DVC**, **lakeFS**, Delta Lake time travel.
- **Lineage:** record which data version trained which model version (Azure ML jobs, SageMaker ML Lineage Tracking, MLflow).
- **Datasheets / data cards:** document source, collection method, intended use, known limits and licence.
- **Licences & consent:** only train on data you have rights to use; respect copyright, privacy law (GDPR, HIPAA, CCPA) and terms of service.

## 11. Data drift

| Type | Meaning | Example |
|---|---|---|
| **Data (covariate) drift** | Input distribution changes | New customer segment, new device type |
| **Concept drift** | Relationship between input and label changes | Fraud patterns evolve |
| **Label drift** | Class balance changes | Fraud rate doubles |
| **Training–serving skew** | Production features computed differently from training | Different scaling code in the API |

Detect with statistical tests (PSI, KS test, Jensen–Shannon) and monitoring: Azure ML model monitoring, SageMaker Model Monitor.

## 12. Cloud tools for training data

| Task | Azure | AWS |
|---|---|---|
| Store raw data | Blob Storage / ADLS Gen2 | Amazon S3 |
| Register and version data | Azure ML data assets (uri_file, uri_folder, **MLTable**) | S3 versioning, SageMaker Feature Store, SageMaker Catalog |
| Labelling | Azure ML data labeling projects | SageMaker Ground Truth / Ground Truth Plus |
| Data prep at scale | Azure Databricks, Microsoft Fabric, Synapse Spark | AWS Glue, EMR, SageMaker Data Wrangler, SageMaker Processing jobs |
| Feature store | Azure ML managed feature store | SageMaker Feature Store |
| Responsible AI on data | Azure ML Responsible AI dashboard | SageMaker Clarify (bias detection) |
| PII detection | Azure AI Language PII detection | Amazon Comprehend PII detection, Amazon Macie |

---

## 💬 Interview questions & answers

**Q1. How do you know your training data is good enough?**
Check quality dimensions (accuracy, completeness, consistency, uniqueness), check representativeness against production, audit a labelled sample, and look at learning curves: if more data still improves validation scores, collect more.

**Q2. How would you build a fine-tuning dataset for a support chatbot?**
Collect real resolved tickets, remove PII, have experts write or correct ideal answers, put them in chat JSONL format, cover edge cases, de-duplicate, split train/validation, and keep a separate human-reviewed evaluation set.

**Q3. What's the difference between data drift and concept drift?**
Data drift: the inputs change (new kinds of customers). Concept drift: the meaning changes (the same behaviour now indicates something else). Both call for monitoring and retraining.

**Q4. How do you prevent duplicates leaking between train and test?**
De-duplicate first (exact and near-duplicate), then use group-aware splitting so related records (same user or document) stay in one split.

**Q5. Is synthetic data safe to use?**
Useful for bootstrapping and rare cases, but it can copy errors and bias. Validate a sample by hand, mix it with real data, and always evaluate on real held-out data.

**Q6. What is training–serving skew and how do you avoid it?**
Features are computed differently at training and inference time. Avoid it by using the same pipeline code (or a feature store) for both, and by monitoring input distributions.

**Q7. RAG documents vs training data: what's the difference?**
Training data changes the model's weights (permanent, costly to update). RAG documents are retrieved at query time and added to the prompt (easy to update, citable). Use RAG for knowledge, and fine-tuning for behaviour or format.

---

## ✅ Final revision checklist

- [ ] I can list seven data quality dimensions.
- [ ] I know four ways to label data and how to control label quality.
- [ ] I can explain leakage, group-aware splits and time-based splits.
- [ ] I can write a chat-format JSONL fine-tuning example and validate it.
- [ ] I can explain data drift vs concept drift vs training–serving skew.
- [ ] I can name the Azure and AWS services for storing, labelling, versioning and monitoring data.

## 🔗 Official docs
- Azure ML data assets: https://learn.microsoft.com/azure/machine-learning/how-to-create-data-assets
- Amazon SageMaker Ground Truth: https://docs.aws.amazon.com/sagemaker/latest/dg/sms.html
- Hugging Face Datasets: https://huggingface.co/docs/datasets

---
*My AI Engineering Study Notes* | [⬅ Previous](03-deep-learning-and-transformers.md) | [🏠 Home](../README.md) | [Next ➡](05-generative-ai-and-prompt-engineering.md)

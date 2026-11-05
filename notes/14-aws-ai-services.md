# AWS AI & Data Services – Complete Developer Study Notes ☁️🟧

> On AWS, GenAI centres on Amazon Bedrock (models, knowledge bases, guardrails, agents) and Bedrock AgentCore (running agents in production). Custom ML centres on Amazon SageMaker AI. Learn these three and the supporting cast.

[⬅ Previous: Azure AI Services](13-azure-ai-services.md) | [🏠 Home](../README.md) | [Next: MLOps Fundamentals ➡](15-mlops-fundamentals.md)

## 📚 What's covered

✅ [AWS fundamentals you need first](#1-aws-fundamentals)
✅ [The AWS AI map](#2-the-aws-ai-map)
✅ [Amazon Bedrock: models & the Converse API](#3-amazon-bedrock)
✅ [Bedrock Knowledge Bases (managed RAG)](#4-bedrock-knowledge-bases)
✅ [Bedrock Guardrails](#5-bedrock-guardrails)
✅ [Bedrock Agents, Flows & model customisation](#6-bedrock-agents-flows--customisation)
✅ [Amazon Bedrock AgentCore](#7-amazon-bedrock-agentcore)
✅ [Amazon SageMaker AI & SageMaker Unified Studio](#8-amazon-sagemaker)
✅ [Prebuilt AI services: Textract, Comprehend, Rekognition, Transcribe, Polly, Translate, Lex, Kendra](#9-prebuilt-ai-services)
✅ [Amazon Q](#10-amazon-q)
✅ [Data services: S3, Glue, Athena, Redshift, OpenSearch, DynamoDB, Aurora](#11-data-services)
✅ [Compute & hosting: Lambda, ECS, EKS, App Runner](#12-compute--hosting)
✅ [Security & monitoring](#13-security--monitoring)
✅ [Reference architecture: enterprise RAG/agent on AWS](#14-reference-architecture)
✅ [Azure ↔ AWS service mapping](#15-azure--aws-mapping)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** AWS AI engineers, AWS ML/AI certification candidates, and cloud engineers moving into AI.

---

## 1. AWS fundamentals

| Concept | Meaning |
|---|---|
| **Account** | Billing and resource boundary (many companies use multi-account setups with AWS Organizations) |
| **Region / Availability Zone** | Location / isolated datacentres within it (model availability varies by region) |
| **IAM** | Users, **roles** and **policies** (JSON) controlling who can do what. Services use **roles**, never hard-coded keys |
| **VPC** | Your private network; **VPC endpoints (PrivateLink)** keep traffic to AWS services private |
| **Service quotas** | Limits (e.g. Bedrock tokens per minute) |

```bash
aws configure            # or: aws configure sso
aws sts get-caller-identity
```

## 2. The AWS AI map

```
 GenAI apps & agents    Amazon Bedrock: Models · Knowledge Bases · Guardrails · Agents · Flows · Evaluations
 Run agents at scale    Amazon Bedrock AgentCore: Runtime · Gateway · Memory · Identity · Observability ·
                        Code Interpreter · Browser
 Custom ML / MLOps      Amazon SageMaker AI (training, tuning, pipelines, registry, endpoints, monitoring)
                        inside Amazon SageMaker Unified Studio (data + analytics + AI in one place)
 Prebuilt AI            Textract · Comprehend · Rekognition · Transcribe · Polly · Translate · Lex · Kendra
 Assistants             Amazon Q Business · Amazon Q Developer
 Data                   S3 · Glue · Athena · Redshift · OpenSearch · DynamoDB · Aurora · Kinesis
 Compute                Lambda · ECS/Fargate · EKS · App Runner · EC2 (GPU, Inferentia, Trainium)
 Platform               IAM · KMS · Secrets Manager · CloudWatch · CloudTrail · API Gateway
```

## 3. Amazon Bedrock

A **fully managed service** for foundation models through one API: no infrastructure to manage, and your data isn't used to train the base models.

- **Models:** Anthropic **Claude**, Amazon **Nova** and **Titan** (embeddings), Meta **Llama**, **Mistral**, **Cohere** (embed/rerank), **DeepSeek**, **AI21**, **Stability AI** (images), and more. Some models must first be **enabled** in the console (**Bedrock → Model access**).
- **Converse API:** one consistent request format across models (messages, tools, streaming), which makes models easy to swap.
- **Inference options:** on-demand (pay per token), **cross-region inference profiles** (more capacity), **batch inference** (cheaper), **provisioned throughput** (reserved), **prompt caching**, **intelligent prompt routing**.

```python
# pip install boto3   (credentials from aws configure / IAM role)
import boto3
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
resp = bedrock.converse(
    modelId="<model-id or inference-profile-id>",          # e.g. a Claude model id from the Bedrock console
    system=[{"text": "You are a concise cloud tutor."}],
    messages=[{"role": "user", "content": [{"text": "What is Amazon Bedrock?"}]}],
    inferenceConfig={"maxTokens": 300, "temperature": 0.2},
)
print(resp["output"]["message"]["content"][0]["text"], resp["usage"])
```

## 4. Bedrock Knowledge Bases

**Managed RAG:** connect data sources → Bedrock parses, chunks, embeds and indexes → query with `Retrieve` or `RetrieveAndGenerate`, with **citations**.

| Piece | Options |
|---|---|
| Data sources | **S3**, web crawler, Confluence, SharePoint, Salesforce, custom connectors |
| Parsing | Default parser, **Bedrock Data Automation**, or a foundation model as parser (tables, images) |
| Chunking | Fixed-size, hierarchical, semantic, or none / custom via Lambda |
| Embeddings | Amazon Titan Embeddings, Cohere Embed |
| Vector stores | **OpenSearch Serverless** (quick create), Aurora PostgreSQL (pgvector), **S3 Vectors**, Pinecone, Redis, MongoDB Atlas, Neptune Analytics (GraphRAG) |
| Extras | Metadata filtering, hybrid search, **reranking**, query decomposition, structured data (text-to-SQL over Redshift) |

```python
agent_rt = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
resp = agent_rt.retrieve_and_generate(
    input={"text": "How long must my laptop password be?"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {"knowledgeBaseId": "<KB_ID>", "modelArn": "<model-arn>"},
    },
)
print(resp["output"]["text"])
for c in resp["citations"]:
    print([ref["location"] for ref in c["retrievedReferences"]])
```

## 5. Bedrock Guardrails

Configurable safety layer applied to model inputs and outputs (works with any Bedrock model, and via the `ApplyGuardrail` API with any model):
- **Content filters** (hate, violence, sexual, misconduct, **prompt attacks**)
- **Denied topics** ("no investment advice")
- **Word filters** and profanity
- **Sensitive information filters**: PII block/mask, custom regex
- **Contextual grounding check**: blocks answers not grounded in the source or irrelevant to the query (hallucination control for RAG)
- **Automated Reasoning checks**: verify answers against formal policy rules

## 6. Bedrock Agents, Flows & customisation

| Feature | What it does |
|---|---|
| **Bedrock Agents** | Managed agents: instructions + **action groups** (Lambda or OpenAPI) + knowledge bases + memory; supports multi-agent collaboration and return-of-control |
| **Bedrock Flows** | Visual workflows linking prompts, models, knowledge bases, Lambda and conditions |
| **Prompt Management** | Versioned, reusable prompts |
| **Model customisation** | Fine-tuning, continued pre-training, **distillation**, reinforcement fine-tuning for supported models; **Custom Model Import** for your own open-weight models |
| **Model evaluation** | Automatic (LLM-as-a-judge) and human evaluation jobs, plus Knowledge Base (RAG) evaluation |

## 7. Amazon Bedrock AgentCore

**AgentCore** = enterprise infrastructure to **deploy and operate agents built with any framework** (LangGraph, LangChain, CrewAI, LlamaIndex, Strands Agents, OpenAI Agents SDK...) and any model.

| Component | What it does |
|---|---|
| **Runtime** | Serverless, session-isolated hosting for agents and MCP/A2A servers; long-running sessions |
| **Gateway** | Turns APIs, Lambda functions and services into **MCP-compatible tools**; tool discovery |
| **Memory** | Managed short-term and long-term memory |
| **Identity** | Agent identity and access: inbound auth plus outbound OAuth/API keys to third-party tools; works with Cognito, Okta, Entra ID |
| **Observability** | OpenTelemetry tracing and dashboards (CloudWatch) for agent steps, tools and tokens |
| **Code Interpreter** | Sandboxed code execution |
| **Browser** | Managed cloud browser for web-automation agents |
| **Policy & Evaluations** | Guard tool calls with policies; continuously evaluate agent quality (newer capabilities; check availability) |

**Strands Agents** is AWS's open-source agent SDK (model-driven, MCP-native); it deploys naturally to AgentCore.

**Bedrock Agents vs AgentCore:** Bedrock Agents = a configured, fully managed agent (less code). AgentCore = run *your own* agent code with production infrastructure (more control, any framework).

## 8. Amazon SageMaker

| Name | What it is |
|---|---|
| **Amazon SageMaker AI** | The ML service (formerly just "Amazon SageMaker"): notebooks, training, tuning, **Pipelines**, **Model Registry**, endpoints, **Model Monitor**, **Clarify**, **JumpStart**, **HyperPod**, managed **MLflow** |
| **Amazon SageMaker Unified Studio** | The next-generation unified environment for data, analytics and AI: SQL analytics, data processing, model development, and **Bedrock** capabilities, governed by the **SageMaker Catalog** over a **lakehouse** (S3 + Redshift) |

Details and code in **[MLOps on AWS](17-mlops-on-aws.md)**.

## 9. Prebuilt AI services

| Service | What it does | Typical use |
|---|---|---|
| **Amazon Textract** | OCR plus forms, tables, queries, invoices/IDs | Parse documents for RAG and automation |
| **Amazon Comprehend** | NLP: entities, sentiment, key phrases, **PII detection**, custom classification | Ticket routing, PII redaction |
| **Amazon Rekognition** | Image/video analysis: labels, faces, text, moderation | Content moderation, media search |
| **Amazon Transcribe** | Speech-to-text (call analytics, medical) | Call centre insights |
| **Amazon Polly** | Text-to-speech | Voice responses |
| **Amazon Translate** | Machine translation | Multilingual content |
| **Amazon Lex** | Chatbots and voice bots (the technology behind Alexa) | IVR and contact-centre bots |
| **Amazon Kendra** | Enterprise intelligent search with connectors | Search across SharePoint and Confluence; RAG retriever |
| **Amazon Personalize / Forecast** | Recommendations / time-series forecasting | Retail recommendations, demand planning |
| **Bedrock Data Automation** | GenAI-powered extraction from documents, images, audio, video | Intelligent document processing |

## 10. Amazon Q

- **Amazon Q Business**: a GenAI assistant over company data (40+ connectors), with access-control awareness.
- **Amazon Q Developer**: an AI coding assistant in IDEs, the CLI and the AWS console (code generation, transformation, troubleshooting).

## 11. Data services

| Service | Role in AI |
|---|---|
| **Amazon S3** | The data lake: datasets, documents, model artifacts; **S3 Vectors** for low-cost vector storage |
| **AWS Glue** | Serverless ETL and the **Data Catalog** |
| **Amazon Athena** | SQL directly on S3 |
| **Amazon Redshift** | Data warehouse (Redshift ML) |
| **Amazon EMR** | Managed Spark/Hadoop |
| **Amazon OpenSearch Service / Serverless** | Search and **vector** database (default store for Bedrock KBs) |
| **Amazon Aurora PostgreSQL / RDS** | Relational DB with **pgvector** |
| **Amazon DynamoDB** | NoSQL key-value store: chat history, agent state |
| **Amazon Kinesis / MSK** | Streaming data |
| **AWS Lake Formation** | Data lake permissions and governance |

## 12. Compute & hosting

| Service | Use for AI apps |
|---|---|
| **AWS Lambda** | Serverless functions: agent tools/action groups, ingestion triggers |
| **Amazon ECS + Fargate** | Serverless containers: AI APIs, agents, MCP servers |
| **Amazon EKS** | Managed Kubernetes for large platforms and GPU inference |
| **AWS App Runner** | Simplest container web-app hosting |
| **Amazon EC2** | VMs: GPU (P/G instances), **AWS Inferentia** (inference) and **Trainium** (training) chips |
| **Amazon API Gateway** | APIs with auth, throttling and usage plans |
| **AWS Step Functions** | Orchestrate workflows (ML pipelines, document processing) |
| **Amazon ECR** | Container image registry |

## 13. Security & monitoring

| Service | Purpose |
|---|---|
| **IAM** (roles, least privilege) | Access control; services assume roles |
| **AWS KMS** | Encryption keys |
| **AWS Secrets Manager** | API keys and DB passwords |
| **VPC endpoints (PrivateLink)** | Private access to Bedrock, S3 and SageMaker |
| **Amazon Cognito** | User sign-in for apps |
| **Amazon CloudWatch** | Metrics, logs, alarms; Bedrock invocation metrics; AgentCore observability |
| **AWS CloudTrail** | Audit of every API call |
| **Amazon Macie** | Find sensitive data in S3 |
| **AWS Budgets / Cost Explorer** | Cost alerts and analysis |

## 14. Reference architecture

```
 Users (web / Slack / Teams) ──► Amazon Cognito (sign-in)
        │
        ▼
 Amazon API Gateway (auth, throttling)
        │
        ▼
 Agent on Bedrock AgentCore Runtime (LangGraph / Strands)   or   Bedrock Agent
   ├── Bedrock models (Claude / Nova) ◄── Bedrock Guardrails (PII, prompt attacks, grounding)
   ├── Bedrock Knowledge Base ◄── S3 / SharePoint / Confluence  (Textract or BDA parsing, Titan embeddings,
   │                                                              OpenSearch Serverless vectors, rerank)
   ├── AgentCore Gateway → tools (Lambda, internal APIs as MCP)
   ├── AgentCore Memory / DynamoDB (state)
   └── AgentCore Identity (OAuth to SaaS tools)
 IAM roles · KMS · VPC endpoints · CloudWatch + AgentCore Observability · CloudTrail · Bedrock evaluations
```

## 15. Azure ↔ AWS mapping

| Need | Azure | AWS |
|---|---|---|
| Foundation models | Foundry Models / Azure OpenAI | Amazon Bedrock |
| Managed RAG | Foundry IQ / file search, Azure AI Search | Bedrock Knowledge Bases |
| Vector/hybrid search | Azure AI Search | OpenSearch Service, Kendra |
| Guardrails | Azure AI Content Safety | Bedrock Guardrails |
| Managed agents | Foundry Agent Service | Bedrock Agents / AgentCore |
| Custom ML platform | Azure Machine Learning | Amazon SageMaker AI |
| AutoML | Azure ML AutoML | SageMaker Autopilot (in Canvas) |
| Document AI | Document Intelligence | Textract / Bedrock Data Automation |
| NLP | AI Language | Comprehend |
| Speech | AI Speech | Transcribe / Polly |
| Vision | AI Vision | Rekognition |
| Object storage / data lake | Blob / ADLS Gen2 | S3 |
| Serverless functions | Azure Functions | AWS Lambda |
| Serverless containers | Container Apps | ECS Fargate / App Runner |
| Kubernetes | AKS | EKS |
| Identity | Entra ID + Managed Identity | IAM roles + Cognito |
| Secrets | Key Vault | Secrets Manager |
| Monitoring | Azure Monitor / App Insights | CloudWatch / X-Ray |
| Low-code assistants | Copilot Studio / M365 Copilot | Amazon Q Business |

---

## 💬 Interview questions & answers

**Q1. Bedrock vs SageMaker AI: when do you use each?**
Bedrock to *consume* foundation models via API (GenAI apps, RAG, agents) with no infrastructure. SageMaker AI to *build, train, tune and host* your own models with full control, or to host open models you need to customise deeply.

**Q2. How do you build RAG on AWS?**
Documents in S3 (or connectors) → Bedrock Knowledge Base (parsing, chunking, Titan/Cohere embeddings, OpenSearch Serverless or S3 Vectors) → `RetrieveAndGenerate` with metadata filters, hybrid search and reranking → Guardrails contextual grounding → citations to the user → Bedrock RAG evaluation.

**Q3. Bedrock Agents vs Bedrock AgentCore?**
Bedrock Agents is a fully managed agent you configure (instructions, action groups, knowledge bases). AgentCore is infrastructure to deploy and operate your own agent code from any framework, with runtime, gateway, memory, identity and observability.

**Q4. How do you secure a Bedrock application?**
IAM least-privilege roles (no access keys in code), VPC endpoints, KMS encryption, Guardrails for content and PII, Secrets Manager, CloudTrail auditing, and Cognito/API Gateway for user auth.

**Q5. What is the Converse API and why use it?**
A unified Bedrock API for chat across models, with a consistent format for messages, tool use, streaming and images. It makes models interchangeable and simplifies code.

**Q6. How do you reduce Bedrock costs?**
Choose smaller models where they pass evaluation, use prompt caching, batch inference for offline jobs, intelligent prompt routing, provisioned throughput only for steady high volume, shorter prompts and fewer retrieved chunks, and monitor token usage in CloudWatch.

---

## ✅ Final revision checklist

- [ ] I can explain IAM roles, VPC endpoints and service quotas.
- [ ] I can call a Bedrock model with the Converse API.
- [ ] I know the Bedrock Knowledge Base pipeline and vector store options.
- [ ] I can list Guardrails features, including contextual grounding.
- [ ] I can name the AgentCore components and compare them with Bedrock Agents.
- [ ] I can explain SageMaker AI vs SageMaker Unified Studio.
- [ ] I can name eight prebuilt AI services and their uses.
- [ ] I can map Azure services to AWS services.

## 🔗 Official docs
- Amazon Bedrock: https://docs.aws.amazon.com/bedrock/
- Amazon Bedrock AgentCore: https://docs.aws.amazon.com/bedrock-agentcore/
- Amazon SageMaker AI: https://docs.aws.amazon.com/sagemaker/
- AWS Well-Architected Generative AI Lens: https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/

---
*My AI Engineering Study Notes* | [⬅ Previous](13-azure-ai-services.md) | [🏠 Home](../README.md) | [Next ➡](15-mlops-fundamentals.md)

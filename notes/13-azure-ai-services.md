# Azure AI & Data Services – Complete Developer Study Notes ☁️🔷

> On Azure, almost every AI project uses the same handful of services: Microsoft Foundry for models and agents, Azure AI Search for retrieval, Azure Machine Learning for custom models, plus storage, identity and monitoring.

[⬅ Previous: LangGraph](12-langgraph.md) | [🏠 Home](../README.md) | [Next: AWS AI Services ➡](14-aws-ai-services.md)

## 📚 What's covered

✅ [Azure fundamentals you need first](#1-azure-fundamentals)
✅ [The Azure AI map](#2-the-azure-ai-map)
✅ [Microsoft Foundry: models, agents, evaluation](#3-microsoft-foundry)
✅ [Azure OpenAI in Foundry Models](#4-azure-openai-in-foundry-models)
✅ [Foundry Agent Service](#5-foundry-agent-service)
✅ [Azure AI Search](#6-azure-ai-search)
✅ [Foundry Tools (formerly Azure AI services): Vision, Speech, Language, Translator, Document Intelligence, Content Safety](#7-foundry-tools-prebuilt-ai)
✅ [Azure Machine Learning](#8-azure-machine-learning)
✅ [Data services: Storage, Fabric, Databricks, Cosmos DB, SQL](#9-data-services)
✅ [Compute & hosting: Functions, Container Apps, AKS, App Service](#10-compute--hosting)
✅ [Security & identity: Entra ID, Managed Identity, Key Vault, Private Link](#11-security--identity)
✅ [Monitoring: Azure Monitor & Application Insights](#12-monitoring)
✅ [Copilot Studio & Microsoft 365 Copilot](#13-copilot-studio--m365-copilot)
✅ [Reference architecture: enterprise RAG/agent on Azure](#14-reference-architecture)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** Azure AI engineers, AI-102 / AI-300 / DP-100 candidates, and cloud engineers moving into AI.

---

## 1. Azure fundamentals

| Concept | Meaning |
|---|---|
| **Tenant** | Your organisation's Microsoft Entra ID directory |
| **Subscription** | Billing and access boundary |
| **Resource group** | Folder for related resources; delete it to delete everything inside |
| **Region** | Datacentre location (model availability differs by region!) |
| **RBAC** | Role-based access: Owner, Contributor, Reader, plus service roles such as *Azure AI User* or *Search Index Data Reader* |
| **Resource provider** | A service's API namespace; must be **registered** in the subscription (e.g. `Microsoft.CognitiveServices`) |
| **Quota** | Limits per region (vCPUs, model tokens-per-minute) |

```bash
az login
az account set --subscription "<name or id>"
az group create -n rg-ai-lab -l eastus2
az provider register --namespace Microsoft.CognitiveServices
```

## 2. The Azure AI map

```
                         ┌──────────────── Microsoft Foundry (ai.azure.com) ────────────────┐
 Build GenAI apps/agents │ Foundry Models (Azure OpenAI, Claude, Llama, Mistral, Phi, ...)  │
                         │ Foundry Agent Service · Evaluations · Tracing · Guardrails       │
                         │ Foundry Tools (Vision, Speech, Language, Document Intelligence...)│
                         └───────────────────────────────────────────────────────────────────┘
 Retrieval               Azure AI Search (vector + keyword + semantic ranker)
 Custom ML / MLOps       Azure Machine Learning (training, AutoML, pipelines, registries, endpoints)
 Data                    Blob/ADLS Gen2 · Microsoft Fabric · Azure Databricks · Cosmos DB · Azure SQL · PostgreSQL
 Run your code           Functions · Container Apps · AKS · App Service
 Low-code / M365         Copilot Studio · Microsoft 365 Copilot · Power Platform
 Platform                Entra ID · Key Vault · Private Link · Azure Monitor / App Insights · API Management
```

## 3. Microsoft Foundry

**Microsoft Foundry** (formerly Azure AI Foundry / Azure AI Studio) is Azure's unified platform for building generative AI apps and agents, at **https://ai.azure.com**.

| Building block | What it does |
|---|---|
| **Foundry resource** | The Azure resource that holds models, agents and connections (resource type: Azure AI services / `Microsoft.CognitiveServices`) |
| **Project** | Workspace inside a Foundry resource for a team or app: agents, files, evaluations |
| **Foundry Models** | Model catalogue and deployments: Azure OpenAI models plus partner and open models (Anthropic Claude, Meta Llama, Mistral, DeepSeek, Microsoft Phi, Cohere...) |
| **Agent Service** | Build, run and publish agents ([section 5](#5-foundry-agent-service)) |
| **Foundry IQ** | Managed knowledge bases for grounding agents (built on Azure AI Search) |
| **Evaluations** | Quality and safety evaluators: groundedness, relevance, coherence, violence, jailbreak, and more |
| **Tracing & monitoring** | OpenTelemetry traces, connected to Application Insights |
| **Guardrails / content filters** | Built-in Azure AI Content Safety filters per deployment |
| **Playgrounds** | Try models and agents without code |

```python
# pip install azure-ai-projects azure-identity
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(endpoint="https://<resource>.services.ai.azure.com/api/projects/<project>",
                          credential=DefaultAzureCredential())
openai_client = project.get_openai_client()
resp = openai_client.responses.create(model="<deployment-name>", input="Explain Azure AI Search in one line.")
print(resp.output_text)
```

## 4. Azure OpenAI in Foundry Models

- OpenAI models (GPT chat/reasoning models, embeddings, image, audio) hosted by Microsoft with **Azure security, compliance, private networking and regional data residency**. Your prompts aren't used to train the models.
- **Deployment types:** *Standard* (pay per token, regional), *Global Standard* (routes globally for capacity), *Data Zone* (EU/US data boundary), *Provisioned (PTU)* (reserved throughput for predictable latency), *Batch* (cheaper, asynchronous).
- **Quota** is measured in **tokens per minute (TPM)** per region and model.
- Use **keyless auth** (Entra ID + Managed Identity, role *Cognitive Services OpenAI User*) instead of API keys.
- **Fine-tuning** is available for supported models (JSONL chat format; [note 04](04-training-data.md#8-fine-tuning-dataset-formats)).

## 5. Foundry Agent Service

A managed service to build and run agents: it handles the conversation state, tool calling and orchestration, with enterprise security.

| Feature | Detail |
|---|---|
| **Agent definition** | Model + instructions + tools |
| **Tools** | File search (RAG on uploaded files), Azure AI Search, Foundry IQ, code interpreter, Bing grounding, OpenAPI tools, Azure Functions, **MCP servers**, **A2A** agents, Logic Apps, browser automation, computer use |
| **Conversations/threads** | Managed conversation history |
| **Multi-agent** | Connected agents and workflows |
| **Publishing** | **Publish to Microsoft Teams & Microsoft 365 Copilot** (via Azure Bot Service), web apps, APIs |
| **Identity** | Microsoft Entra Agent ID for agent identities; on-behalf-of user auth |
| **Observability** | Tracing, evaluations, monitoring |


## 6. Azure AI Search

Azure's managed **search and retrieval** engine: the default vector store for RAG on Azure.

| Capability | Detail |
|---|---|
| **Index** | Schema of fields (text, vector, filterable metadata) |
| **Indexers** | Pull and refresh data automatically from Blob, ADLS, SQL, Cosmos DB, SharePoint and more |
| **Skillsets** | AI enrichment during indexing: OCR, chunking, embedding (**integrated vectorisation**), entity extraction |
| **Search types** | Keyword (BM25), **vector** (HNSW), **hybrid** (RRF), **semantic ranker** (cross-encoder reranking + captions) |
| **Agentic retrieval** | LLM-assisted query planning across multiple sub-queries (basis of Foundry IQ) |
| **Security** | Entra RBAC, private endpoints, **security trimming** via filterable ACL fields / document-level permissions |
| **Pricing tiers** | Free (testing), Basic, Standard S1–S3, Storage Optimized |

```python
# pip install azure-search-documents
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.identity import DefaultAzureCredential

client = SearchClient("https://<search>.search.windows.net", "policies", DefaultAzureCredential())
results = client.search(
    search_text="laptop password length",                                   # keyword part
    vector_queries=[VectorizableTextQuery(text="laptop password length", k_nearest_neighbors=20,
                                          fields="content_vector")],         # vector part → hybrid
    query_type="semantic", semantic_configuration_name="default",           # semantic reranking
    filter="department eq 'IT'", top=5,
)
for r in results:
    print(r["title"], r["@search.reranker_score"])
```

## 7. Foundry Tools (prebuilt AI)

Formerly **Azure AI services / Cognitive Services**: ready-made AI APIs, no training needed.

| Service | What it does | Typical use |
|---|---|---|
| **Azure AI Document Intelligence** | Extracts text, tables, key-value pairs and layout; prebuilt models for invoices, receipts, IDs; custom models | Parse PDFs for RAG, automate forms |
| **Azure AI Vision** | Image analysis, OCR, captions, face detection (restricted) | Image tagging, read text from photos |
| **Azure AI Speech** | Speech-to-text, text-to-speech, translation, real-time voice | Call centre transcription, voice bots |
| **Azure AI Language** | Sentiment, entities, **PII detection**, summarisation, conversational language understanding, custom Q&A | Redact PII, classify tickets |
| **Azure AI Translator** | Text and document translation (100+ languages) | Multilingual apps |
| **Azure AI Content Safety** | Detects harmful content; **Prompt Shields** (jailbreak/indirect injection); **groundedness detection**; protected material | Guardrails for LLM apps |
| **Azure AI Content Understanding** | Multimodal extraction from documents, images, audio and video into structured output | Video/call analytics, document pipelines |

## 8. Azure Machine Learning

The platform for **custom ML and MLOps**: data, training, tracking, registries, deployment and monitoring. Full details in **[MLOps on Azure](16-mlops-on-azure.md)**.

| Asset | Purpose |
|---|---|
| Workspace | Top-level container (storage, Key Vault, App Insights, ACR) |
| Compute instance / cluster / serverless | Dev VM / autoscaling training cluster / on-demand compute |
| Data assets & datastores | Versioned data references (uri_file, uri_folder, MLTable) |
| Environments | Docker + conda definitions for reproducible runs |
| Jobs | Command, sweep, pipeline and AutoML jobs, tracked with **MLflow** |
| Models & registries | Versioned models, shared across workspaces |
| Online / batch endpoints | Real-time and batch inference |
| Prompt flow | Orchestrating and evaluating LLM flows |


## 9. Data services

| Service | What it does |
|---|---|
| **Azure Blob Storage / ADLS Gen2** | Object storage / data lake with hierarchical namespace: raw data, documents, model artifacts |
| **Microsoft Fabric** | All-in-one SaaS analytics: OneLake, data engineering, warehouses, Power BI, real-time intelligence |
| **Azure Databricks** | Apache Spark lakehouse: big data processing, ML, Delta Lake, MLflow |
| **Azure Synapse Analytics** | Data warehousing and Spark (Fabric is the newer direction) |
| **Azure Data Factory** | ETL/ELT pipelines, 90+ connectors |
| **Azure Cosmos DB** | Globally distributed NoSQL with **vector search**: chat history, agent memory, operational data |
| **Azure SQL / Azure Database for PostgreSQL** | Relational databases; PostgreSQL supports **pgvector** |
| **Azure Event Hubs** | Streaming ingestion (telemetry, logs) |

## 10. Compute & hosting

| Service | Use for AI apps |
|---|---|
| **Azure Functions** | Serverless event-driven code: tools for agents, ingestion triggers |
| **Azure Container Apps** | Serverless containers: **default choice** to host AI APIs, agents and MCP servers; scale to zero |
| **Azure Kubernetes Service (AKS)** | Full Kubernetes: large platforms, GPU inference (with KAITO), complex microservices |
| **Azure App Service** | Managed web apps and APIs (chat front-ends) |
| **Azure API Management** | API gateway: auth, rate limits, **AI gateway** (token limits, load-balancing across model deployments, semantic caching), MCP server exposure |
| **Azure Container Registry (ACR)** | Store Docker images |

## 11. Security & identity

| Service | Purpose |
|---|---|
| **Microsoft Entra ID** | Identity for users, apps and agents (SSO, MFA, Conditional Access) |
| **Managed Identity** | Gives an Azure resource an identity, so there are **no secrets in code** (`DefaultAzureCredential`) |
| **Azure Key Vault** | Secrets, keys and certificates |
| **Private Link / Private Endpoints** | Access services over a private network, no public internet |
| **Microsoft Defender for Cloud** | Security posture, including AI threat protection |
| **Microsoft Purview** | Data governance, classification, DLP for AI interactions |
| **Azure Policy** | Enforce rules (allowed regions, required tags, no public endpoints) |

## 12. Monitoring

- **Azure Monitor** (metrics and logs) + **Log Analytics** (KQL queries).
- **Application Insights**: app telemetry and **OpenTelemetry traces of LLM and agent calls** (connected to Foundry tracing).
- Track: latency, errors, **tokens per request**, cost, content-filter hits, evaluation scores.
- **Cost Management + Budgets** for spend alerts.

## 13. Copilot Studio & M365 Copilot

| Product | What it is |
|---|---|
| **Microsoft 365 Copilot** | The AI assistant in Word, Excel, Outlook, Teams; extensible with **agents** |
| **Copilot Studio** | Low-code builder for agents and copilots (topics, knowledge, actions, connectors); publishes to Teams, M365 Copilot and websites |
| **Teams AI / Microsoft 365 Agents SDK** | Pro-code SDKs for agents in Teams and M365 |

**Pro-code vs low-code:** Foundry Agent Service for custom, complex, developer-built agents; Copilot Studio for business-built agents with connectors. They can be combined (a Copilot Studio agent calling a Foundry agent).

## 14. Reference architecture

```
 Users (Teams / M365 Copilot / Web app) ──► Entra ID (SSO)
        │
        ▼
 Azure API Management (AI gateway: auth, token limits, caching)
        │
        ▼
 Agent / RAG API on Azure Container Apps  (LangGraph or Foundry Agent Service)
   ├── Foundry Models (Azure OpenAI / Claude) ◄── Content Safety (Prompt Shields, groundedness)
   ├── Azure AI Search (hybrid + semantic ranker, security trimming) ◄── indexer ◄── Blob / SharePoint
   │                                           ▲ Document Intelligence (parse) + embeddings
   ├── Tools: Azure Functions / MCP servers / Logic Apps
   └── Memory: Cosmos DB
 Managed Identity → Key Vault · Private Endpoints everywhere · App Insights tracing · Foundry evaluations in CI
```

---

## 💬 Interview questions & answers

**Q1. Microsoft Foundry vs Azure Machine Learning: when do you use each?**
Foundry for generative AI apps and agents: consuming foundation models, RAG, agents, evaluation. Azure ML for building and operating **custom** models: training, AutoML, pipelines, MLOps. Many solutions use both (a custom model in Azure ML called as a tool by a Foundry agent).

**Q2. How do you build RAG on Azure?**
Store documents in Blob/SharePoint → index with Azure AI Search (indexer + skillset for chunking and integrated vectorisation, or Document Intelligence for complex PDFs) → hybrid + semantic ranker retrieval with ACL filters → Azure OpenAI or a Foundry model generates grounded answers → Content Safety groundedness and Prompt Shields → Foundry evaluations and App Insights tracing. Or use Foundry Agent Service with file search / Foundry IQ for a managed approach.

**Q3. How do you avoid API keys in Azure AI apps?**
Use Managed Identity with `DefaultAzureCredential`, give the app least-privilege RBAC roles (e.g. *Cognitive Services OpenAI User*, *Search Index Data Reader*), keep any remaining secrets in Key Vault, and disable local key auth where possible.

**Q4. What's the difference between Standard and Provisioned deployments?**
Standard is pay-per-token with shared capacity (quota in TPM). Provisioned (PTU) reserves throughput for predictable latency and cost at high, steady volume.

**Q5. How do you protect an LLM app from prompt injection on Azure?**
Azure AI Content Safety Prompt Shields (direct and indirect attacks), content filters, groundedness detection, strict system prompts, least-privilege tools, and API Management policies, plus red-teaming with Foundry evaluations.

**Q6. Where would you host an MCP server or agent API?**
Azure Container Apps for most cases (serverless containers, scale to zero, managed identity), AKS for large platforms, Functions for lightweight tools. Front it with API Management for auth and rate limits.

---

## ✅ Final revision checklist

- [ ] I can explain tenant, subscription, resource group, region, RBAC and quota.
- [ ] I can describe Microsoft Foundry's building blocks (resource, project, models, agents, evaluations).
- [ ] I know the Azure OpenAI deployment types and TPM quota.
- [ ] I can list Foundry Agent Service tools, including MCP and A2A.
- [ ] I can explain Azure AI Search: indexers, skillsets, hybrid and semantic ranker.
- [ ] I can name six Foundry Tools (prebuilt AI services) and their uses.
- [ ] I can draw the enterprise RAG/agent reference architecture on Azure.
- [ ] I can explain keyless auth with Managed Identity.

## 🔗 Official docs
- Microsoft Foundry: https://learn.microsoft.com/azure/ai-foundry/
- Azure AI Search: https://learn.microsoft.com/azure/search/
- Azure Machine Learning: https://learn.microsoft.com/azure/machine-learning/
- Azure Architecture Center (AI): https://learn.microsoft.com/azure/architecture/ai-ml/

---
*My AI Engineering Study Notes* | [⬅ Previous](12-langgraph.md) | [🏠 Home](../README.md) | [Next ➡](14-aws-ai-services.md)

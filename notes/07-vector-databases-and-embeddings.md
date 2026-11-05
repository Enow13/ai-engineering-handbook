# Embeddings & Vector Databases – Complete Developer Study Notes 🧭🗄️

> An embedding turns meaning into numbers. A vector database finds the closest meanings in milliseconds, across millions of items.

[⬅ Previous: RAG](06-rag.md) | [🏠 Home](../README.md) | [Next: Agentic AI ➡](08-agentic-ai.md)

## 📚 What's covered

✅ [What embeddings are](#1-what-embeddings-are)
✅ [Similarity metrics](#2-similarity-metrics)
✅ [Choosing an embedding model](#3-choosing-an-embedding-model)
✅ [What a vector database does](#4-what-a-vector-database-does)
✅ [Index types: Flat, HNSW, IVF, PQ](#5-index-types)
✅ [Vector DB comparison: FAISS, Chroma, Pinecone, Qdrant, Weaviate, Milvus, pgvector & cloud options](#6-vector-database-comparison)
✅ [Metadata filtering & hybrid search](#7-metadata-filtering--hybrid-search)
✅ [Scaling, cost & operations](#8-scaling-cost--operations)
✅ [Code example](#9-code-example)
✅ [Interview questions & answers](#-interview-questions--answers)
✅ [Final revision checklist](#-final-revision-checklist)

🎯 **Perfect for:** RAG engineers, search engineers, and GenAI developers.

---

## 1. What embeddings are

An **embedding** is a list of numbers (a vector, often 384–3,072 dimensions) that represents the **meaning** of text, an image or audio. Similar meanings end up close together in vector space.

```
"reset my password"      → [0.12, -0.40, 0.88, ...]  ┐  close together
"I forgot my login"      → [0.10, -0.37, 0.91, ...]  ┘
"quarterly sales report" → [-0.65, 0.22, 0.05, ...]     far away
```

**Types:** text embeddings, multimodal embeddings (text and images in the same space), **sparse** embeddings (SPLADE: keyword-like), and **late-interaction** models (ColBERT: one vector per token, more precise).

## 2. Similarity metrics

| Metric | Formula idea | Notes |
|---|---|---|
| **Cosine similarity** | Angle between vectors | Most common for text; ignores length |
| **Dot product** | Sum of element products | Same as cosine when vectors are normalised; fastest |
| **Euclidean (L2)** | Straight-line distance | Lower = more similar |

⚠️ Use the **metric the embedding model was trained for** (check its model card), and always use the **same embedding model** for documents and queries.

## 3. Choosing an embedding model

| Factor | Consider |
|---|---|
| Quality | Check the **MTEB** leaderboard *and* test on your own data |
| Language & domain | Multilingual? Legal, medical, or code text? |
| Dimensions | Higher = more nuance, but more storage and slower search. Some models allow shortening (Matryoshka) |
| Max input length | Must fit your chunk size |
| Cost & hosting | API (Azure OpenAI, Bedrock Titan/Cohere) vs open-source self-hosted (bge, e5, gte, nomic) |
| Data residency | Region and privacy requirements |

💡 Changing the embedding model means **re-embedding every document**. Plan for it, and version your index.

## 4. What a vector database does

1. **Stores** vectors plus metadata plus (often) the original text.
2. **Indexes** them for fast **Approximate Nearest Neighbour (ANN)** search.
3. **Queries:** "give me the top-k vectors closest to this one, where department = HR".
4. **Manages data:** CRUD, upserts, replication, backups, access control, scaling.

**Exact (brute-force) search** compares against every vector: perfect recall, but slow at scale. **ANN** trades a little recall for big speed-ups.

## 5. Index types

| Index | How it works | Pros | Cons |
|---|---|---|---|
| **Flat** | Compare against all vectors | 100% recall | Slow for millions |
| **HNSW** | Multi-layer graph; "navigable small world" hops toward neighbours | Fast, high recall, **most popular** | Memory-hungry |
| **IVF** | Cluster vectors; search only the nearest clusters | Good for large datasets | Tune `nlist` and `nprobe` |
| **PQ / scalar / binary quantisation** | Compress vectors | Huge memory savings | Some recall loss (rescore to recover) |
| **DiskANN** | Graph index stored on SSD | Billions of vectors, cheaper | More complex |

**HNSW knobs:** `M` (links per node), `ef_construction` (build quality), `ef_search` (query accuracy vs speed).

## 6. Vector database comparison

| Option | Type | Best for |
|---|---|---|
| **FAISS** (Meta) | Library, in-process | Fast local or research search; you manage persistence |
| **Chroma** | Lightweight open-source DB | Prototypes, local development |
| **Pinecone** | Fully managed SaaS | Production without running infrastructure; serverless |
| **Qdrant** | Open-source + cloud (Rust) | Rich filtering, performance, self-host or managed |
| **Weaviate** | Open-source + cloud | Built-in hybrid search and vectorisation modules |
| **Milvus / Zilliz** | Open-source distributed + cloud | Very large scale |
| **pgvector** (PostgreSQL) | Extension | You already use Postgres; SQL + vectors together |
| **Elasticsearch / OpenSearch** | Search engines with vector support | Hybrid keyword + vector at scale |
| **Azure AI Search** | Azure managed | Hybrid + semantic ranker + Azure integration + security trimming |
| **Azure Cosmos DB / Azure Database for PostgreSQL** | Azure managed DBs with vector search | Operational data + vectors |
| **Amazon OpenSearch Service / Serverless** | AWS managed | Default vector store for Bedrock Knowledge Bases |
| **Aurora PostgreSQL (pgvector)** | AWS managed | Postgres + vectors |
| **Amazon S3 Vectors** | AWS storage-native vectors | Very large, low-cost vector storage |
| **MongoDB Atlas Vector Search, Redis** | DB/cache with vectors | When already in your stack; Redis for semantic caching |

**How to choose:** prototype → Chroma/FAISS. Production on Azure → Azure AI Search. On AWS → OpenSearch or Bedrock Knowledge Bases. Already on Postgres → pgvector. No infrastructure team → Pinecone or Qdrant Cloud.

## 7. Metadata filtering & hybrid search

- **Pre-filtering:** filter first, then vector search. Accurate, but can be slow if the filter leaves very few items.
- **Post-filtering:** vector search, then filter. Fast, but may return fewer than k results.
- Most modern DBs do **filtered HNSW** efficiently. Check how yours does it.
- **Hybrid search** = vector + keyword (BM25) fused with RRF. Built into Azure AI Search, OpenSearch, Weaviate, Qdrant, Elasticsearch and Pinecone.

## 8. Scaling, cost & operations

| Concern | Practice |
|---|---|
| Memory | Quantise vectors, reduce dimensions, use disk-based indexes |
| Freshness | Incremental upserts; delete vectors of removed documents |
| Multi-tenancy | Namespace/collection per tenant, or a tenant_id filter |
| Re-embedding | Blue/green index: build a new index, switch the alias, delete the old one |
| Backups & DR | Snapshots, replicas across zones |
| Monitoring | Query latency (p95), recall on a test set, index size, cost |
| Security | Network isolation, encryption, RBAC, ACL metadata filters |

## 9. Code example

Local semantic search with **Chroma** (it downloads a small default embedding model on first run):

```python
# pip install chromadb
import chromadb

client = chromadb.Client()                              # in-memory; use PersistentClient(path=...) to save
col = client.create_collection("policies", metadata={"hnsw:space": "cosine"})
col.add(
    ids=["p1", "p2", "p3"],
    documents=["Passwords must be at least 12 characters.",
               "BitLocker encryption is required on laptops.",
               "Remote core hours are 9 AM to 3 PM."],
    metadatas=[{"policy": "it"}, {"policy": "it"}, {"policy": "remote"}],
)
res = col.query(query_texts=["how long should my password be"], n_results=2, where={"policy": "it"})
print(res["documents"], res["distances"])
```

---

## 💬 Interview questions & answers

**Q1. What is an embedding?**
A dense vector that represents meaning, so semantically similar items are close in vector space. It's produced by an embedding model.

**Q2. How does HNSW work?**
It builds a layered graph. Search starts at the sparse top layer, greedily hops toward the query, and descends to denser layers to refine. This gives logarithmic-like search time with high recall.

**Q3. Cosine vs dot product vs Euclidean?**
Cosine measures angle (ignores magnitude); dot product equals cosine for normalised vectors and is fastest; Euclidean measures distance. Use the metric the embedding model was trained with.

**Q4. When would you choose pgvector over a dedicated vector DB?**
When data already lives in Postgres, scale is moderate (up to millions of vectors), and you value transactions, joins and one system to operate. Choose a dedicated DB for very large scale, advanced filtering or hybrid features.

**Q5. How do you handle changing the embedding model?**
Build a new index with the new model alongside the old one, re-embed everything, evaluate recall, switch traffic (alias or blue/green), then retire the old index. Never mix vectors from different models.

**Q6. What is quantisation in vector DBs?**
Compressing vectors (to 8-bit, 4-bit or binary) to cut memory and speed up search, often with a re-scoring step on full-precision vectors to recover accuracy.

**Q7. Pre-filtering vs post-filtering?**
Pre-filtering restricts candidates by metadata before ANN search (accurate, can be slower). Post-filtering searches first, then filters (fast, but may return too few results).

---

## ✅ Final revision checklist

- [ ] I can explain embeddings and the three similarity metrics.
- [ ] I know how to choose an embedding model (MTEB plus my own evaluation).
- [ ] I can explain Flat, HNSW, IVF and quantisation.
- [ ] I can compare FAISS, Chroma, Pinecone, Qdrant, Weaviate, pgvector, Azure AI Search and OpenSearch.
- [ ] I can explain pre- vs post-filtering and hybrid search.
- [ ] I know how to safely switch embedding models.

## 🔗 Official docs
- MTEB leaderboard: https://huggingface.co/spaces/mteb/leaderboard
- Azure AI Search vector search: https://learn.microsoft.com/azure/search/vector-search-overview
- Amazon OpenSearch vector search: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/knn.html

---
*My AI Engineering Study Notes* | [⬅ Previous](06-rag.md) | [🏠 Home](../README.md) | [Next ➡](08-agentic-ai.md)

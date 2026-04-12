---
title: Enterprise Workflow OpenEnv
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🏢 Enterprise Workflow OpenEnv

A real-world **OpenEnv-compatible** environment for training AI agents on enterprise procurement workflows — built for the **Meta × PyTorch × Hugging Face OpenEnv Hackathon** hosted by Scaler School of Technology (SST).

> https://huggingface.co/spaces/MA4KU2/enterprise-workflow-env

> https://ma4ku2-enterprise-workflow-env.hf.space 

---

## 🚀 Overview

**Enterprise Workflow OpenEnv** simulates a realistic enterprise procurement pipeline where AI agents must complete multi-step workflows — from parsing purchase requisitions to drafting purchase orders and flagging approvals.

Designed to benchmark and train agents on **structured decision-making** in real-world business contexts.

---

## 🧩 Tasks

| Difficulty | Description | Steps | Score |
|------------|-------------|-------|-------|
| 🟢 **Easy** | Parse purchase requisition → match correct inventory item | 1 | `0.92` |
| 🟡 **Medium** | Parse requisition → check inventory → draft purchase order | 3 | `0.92` |
| 🔴 **Hard** | Full pipeline: parse → inventory → supplier → PO → approval | 5 | `0.92` |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Reset environment — works with or without body |
| `POST` | `/step` | Execute an agent action and get observation |
| `GET` | `/state/{task_id}` | Get current state for a task |
| `GET` | `/tasks` | List all tasks with action schemas |
| `GET` | `/grader` | Run all graders — returns sigmoid scores in (0,1) |
| `GET` | `/baseline` | Baseline scores for comparison |

---

## 🏗️ Architecture

### Environment Design
- **Financial Guardrails** — validates `total_cost == quantity × unit_price` on every PO draft
- **Prerequisite Enforcement** — agents cannot skip steps (no PO before inventory check)
- **Graceful Error Handling** — unknown actions return `done=False` allowing agent recovery
- **Sigmoid Grading** — smooth scoring strictly within (0, 1) using sigmoid normalization
- **Partial Reward Signals** — rewards at every step, not just episode end

### Agent Design
- **Skill System** — composable, ordered workflow action definitions per task
- **Episode Memory** — remembers past workflow decisions across resets
- **Jittered Backoff Retry** — decorrelated exponential retry on LLM failures
- **Trajectory Compressor** — compresses long episode histories to fit token budgets
- **Observation-Driven Loop** — LLM decides next action based on environment observation

### Action Space
parse_requisition  → payload: {req_id, item_id}
check_inventory    → payload: {item_id}
message_supplier   → payload: {item_id}
draft_po           → payload: {item_id, quantity, total_cost, department}
flag_approval      → payload: {approver}

### Observation Space
```json
{
  "task_id": "easy|medium|hard",
  "step": 0,
  "result": {},
  "reward": 0.0,
  "done": false,
  "info": ""
}
```

---

## 🗂️ Project Structure
```
├── inference.py            # Main inference script (observation-driven LLM agent)
├── openenv.yaml            # OpenEnv configuration
├── Dockerfile              # Container definition (python:3.11-slim, port 7860)
├── requirements.txt        # Dependencies
├── app/
│   ├── main.py             # FastAPI routes and endpoints
│   ├── environment.py      # WorkflowEnvironment — state machine + reward logic
│   ├── models.py           # Pydantic typed models
│   ├── grader.py           # Sigmoid grading logic
│   └── mock_backend.py     # Mock enterprise backend (15 items, 13 requisitions)
├── agent/
│   ├── skills.py           # Composable skill system with episode memory
│   ├── retry_utils.py      # Jittered backoff retry
│   ├── trajectory.py       # Trajectory compressor
│   └── baseline.py         # Multi-episode baseline runner
├── tasks/
│   ├── easy.py             # Easy task definition
│   ├── medium.py           # Medium task definition
│   └── hard.py             # Hard task definition
└── tests/
    ├── final_validation.py # Full environment logic validation (5 tests)
    └── test_with_mock.py   # Mocked LLM tests
```

## ⚡ Quick Start

### Reset Environment
```bash
curl -X POST https://ma4ku2-enterprise-workflow-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "hard"}'
```

### Execute a Step
```bash
curl -X POST https://ma4ku2-enterprise-workflow-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy", "action_type": "parse_requisition", "payload": {"req_id": "REQ-001", "item_id": "ITM-001"}}'
```

### Check Grader Scores
```bash
curl https://ma4ku2-enterprise-workflow-env.hf.space/grader
```

### Run Inference Agent
```bash
export OPENAI_API_KEY="<your_openrouter_key>"
export API_BASE_URL="https://openrouter.ai/api/v1"
export MODEL_NAME="openai/gpt-oss-120b:free"
python3 inference.py
```

---

## 📋 Baseline Scores
```
[START] task=easy env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.99 done=true error=null
[END] success=true steps=1 score=0.990 rewards=0.99
[START] task=medium env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.33 done=false error=null
[STEP] step=2 action=check_inventory reward=0.33 done=false error=null
[STEP] step=3 action=draft_po reward=0.33 done=true error=null
[END] success=true steps=3 score=0.990 rewards=0.33,0.33,0.33
[START] task=hard env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.20 done=false error=null
[STEP] step=2 action=check_inventory reward=0.20 done=false error=null
[STEP] step=3 action=message_supplier reward=0.20 done=false error=null
[STEP] step=4 action=draft_po reward=0.20 done=false error=null
[STEP] step=5 action=flag_approval reward=0.19 done=true error=null
[END] success=true steps=5 score=0.990 rewards=0.20,0.20,0.20,0.20,0.19
```

---

## 💻 Built On Constrained Hardware

Built entirely on a **Raspberry Pi 5 (8GB RAM)** running **Kali Linux (aarch64/ARM64) OS** — no cloud compute, no GPU.

All Docker builds, local testing, and HuggingFace deployments executed directly on ARM64 hardware, proving the environment is lightweight and portable.

---

## 🔑 Zero-Cost Inference Stack

Uses **OpenRouter** as API gateway with free-tier models — entire development pipeline completely free.

Compatible with any OpenAI-compatible endpoint via environment variables:
- `OPENAI_API_KEY` — your API key
- `API_BASE_URL` — swap to any provider
- `MODEL_NAME` — swap to any model

---

## 🗺️ Production Roadmap

### Enterprise Integrations
- Temporal.io for durable long-running workflow execution
- Merge.dev for ERP integration (SAP, Oracle, Workday)
- Pinecone/Supabase for corporate procurement memory via RAG
- LangSmith for LLM observability and audit trails
- NeMo Guardrails for prompt injection protection
- CLI Interface to directly interact with the Agent Directly

### Automation & Orchestration
- n8n for no-code workflow automation layer
- LangFlow for visual agent pipeline builder
- MCP servers for dynamic tool discovery and capability extension

### Agent Infrastructure
- OpenClaw multi-agent orchestration for parallel procurement workflows
- Redis for short-term agent memory and API call caching
- Slack/Teams integration for Human-in-the-Loop approvals

---

## 🛠️ Built With

- **FastAPI** — High-performance API framework
- **OpenEnv** — Environment standard for AI agent training
- **Docker** — Containerized deployment
- **Hugging Face Spaces** — Deployment platform
- **OpenRouter** — Zero-cost LLM inference gateway

---

## 🏆 Hackathon

Submitted to the **Meta PyTorch OpenEnv Hackathon**, hosted by Scaler School of Technology (SST), Hugging Face, PyTorch, and Meta.

---

## 📄 License

MIT License

---
title: Enterprise Workflow OpenEnv
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🏢 Enterprise Workflow OpenEnv

> A real-world **OpenEnv-compatible** environment for training AI agents on enterprise procurement workflows — built for the **Meta × PyTorch × Hugging Face OpenEnv Hackathon** hosted by Scaler School of Technology (SST).

> https://huggingface.co/spaces/MA4KU2/enterprise-workflow-env

> https://ma4ku2-enterprise-workflow-env.hf.space 
---

## 🚀 Overview

**Enterprise Workflow OpenEnv** simulates a realistic enterprise procurement pipeline where AI agents must complete multi-step workflows — from parsing purchase requisitions to drafting purchase orders and flagging approvals.

This environment is designed to benchmark and train agents on **structured decision-making** in real-world business contexts.

## 💻 Built On Constrained Hardware

This entire environment was designed, built, tested, and deployed on a **Raspberry Pi 5 (8GB RAM)** running **Kali Linux OS (aarch64)** with **VERSION - 2026.1** — no cloud compute, no GPU, no high-end development machine.

All Docker builds, local testing, and HuggingFace deployments were executed directly on ARM64 hardware with limited RAM — proving the environment is lightweight, portable, and production-ready.

### ✨ Agent Features

| Feature | Description |
|---------|-------------|
| 🧠 **Skill System** | Composable, reusable workflow action definitions with ordered task chains |
| 💾 **Episode Memory** | Remembers past workflow decisions and rewards across resets |
| ✅ **Payload Validation** | Validates required fields before every action to catch missing data early |
| 🔄 **Jittered Backoff Retry** | Decorrelated exponential retry on LLM failures — no thundering herd |
| 🗜️ **Trajectory Compressor** | Compresses long episode histories to fit token budgets |
| 📊 **Sigmoid Grading** | Smooth scoring strictly within (0, 1) using sigmoid normalization |

---

## 🔑 Zero-Cost Inference Stack

Instead of paid OpenAI API credits, this project uses **OpenRouter** as the API gateway with free-tier models (`openai/gpt-oss-20b:free`) — keeping the entire development and testing pipeline completely free.

The inference script is fully compatible with any OpenAI-compatible endpoint via environment variables:
- `API_BASE_URL` — swap to any provider
- `MODEL_NAME` — swap to any model
<<<<<<< HEAD
- `HF_TOKEN` && `OPENAI_API_KEY`  — your API key
=======
- `HF_THJLKLOKEN` && `OPENAI_API_KEY`  — your API key
>>>>>>> 8e7e41a (fix: graceful unknown action handling)

---

## 🧩 Tasks

| Difficulty | Description | Steps | Score |
|------------|-------------|-------|-------|
| 🟢 **Easy** | Parse purchase requisition → match correct inventory item | 1 | `0.99` |
| 🟡 **Medium** | Parse requisition → check inventory → draft purchase order | 3 | `0.99` |
| 🔴 **Hard** | Full pipeline: parse → inventory → supplier → PO → approval | 5 | `0.99` |

---

## 📋 Inference Output
```
[START] task=easy env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.99 done=true error=null
[END] success=true steps=1 score=0.99 rewards=0.99
[START] task=medium env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.33 done=false error=null
[STEP] step=2 action=check_inventory reward=0.33 done=false error=null
[STEP] step=3 action=draft_po reward=0.33 done=true error=null
[END] success=true steps=3 score=0.99 rewards=0.33,0.33,0.33
[START] task=hard env=enterprise-workflow-env model=openai/gpt-oss-20b:free
[STEP] step=1 action=parse_requisition reward=0.20 done=false error=null
[STEP] step=2 action=check_inventory reward=0.20 done=false error=null
[STEP] step=3 action=message_supplier reward=0.20 done=false error=null
[STEP] step=4 action=draft_po reward=0.20 done=false error=null
[STEP] step=5 action=flag_approval reward=0.19 done=true error=null
[END] success=true steps=5 score=0.99 rewards=0.20,0.20,0.20,0.20,0.19
```

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

## ⚡ Quick Start

### Reset Environment
```bash
# No body needed — defaults to easy task
curl -X POST https://ma4ku2-enterprise-workflow-env.hf.space/reset

# Or specify a task
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
# {"scores": {"easy": 0.9205, "medium": 0.9205, "hard": 0.9205}}
```

### Run Inference Agent
```bash
python3 inference.py
```

---

## 🏗️ Project Structure

```
├── server/
│   └── app.py              # FastAPI server entry point
├── app/
│   ├── main.py             # FastAPI routes
│   ├── environment.py      # WorkflowEnvironment logic
│   ├── models.py           # Pydantic models
│   ├── grader.py           # Sigmoid grading logic
│   ├── mock_backend.py     # Mock enterprise backend
│   └── __init__.py
├── agent/
│   ├── skills.py           # Hermes-inspired skill system with memory
│   ├── retry_utils.py      # Jittered backoff retry (from Hermes)
│   ├── trajectory.py       # Trajectory compressor (from Hermes)
│   ├── baseline.py         # Baseline agent
│   ├── tools.py            # Agent tools
│   └── __init__.py
├── tasks/
│   ├── easy.py             # Easy task definition
│   ├── medium.py           # Medium task definition
│   └── hard.py             # Hard task definition
├── inference.py            # Main inference script
├── openenv.yaml            # OpenEnv configuration
├── pyproject.toml          # Python package config
├── requirements.txt        # Dependencies
└── uv.lock                 # Locked dependencies
```

---

## 🧠 Skill System

The agent uses a **composable skill chain** system inspired by NousResearch's Hermes agent:

```python
TASK_SKILL_CHAINS = {
    "easy":   ["parse_requisition"],
    "medium": ["parse_requisition", "check_inventory", "draft_po"],
    "hard":   ["parse_requisition", "check_inventory", "message_supplier", "draft_po", "flag_approval"],
}
```

Each skill defines required payload fields, applicable tasks, and step order — enabling automatic validation and smarter action selection.

---

## 🛠️ Built With

- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance API framework
- **[PyTorch](https://pytorch.org/)** — Meta's deep learning framework
- **[Hugging Face Spaces](https://huggingface.co/spaces)** — Deployment platform
- **[OpenEnv](https://openenv.dev/)** — Environment standard for AI agent training
- **Docker** — Containerized deployment

---

## 🏆 Hackathon

Submitted to the **Meta PyTorch OpenEnv Hackathon**, hosted by:
- 🏫 [Scaler School of Technology (SST)](https://www.scaler.com/school-of-technology/)
- 🤗 [Hugging Face](https://huggingface.co/)
- 🔥 [PyTorch](https://pytorch.org/)
- 🌐 [Meta](https://ai.meta.com/)

---

## 📄 License

MIT License — feel free to use and build upon this environment.

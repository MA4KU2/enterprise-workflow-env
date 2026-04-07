---
title: Enterprise Workflow OpenEnv
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🏢 Enterprise Workflow OpenEnv

> A real-world **OpenEnv-compatible** environment for training AI agents on enterprise procurement workflows — built for the **Meta × PyTorch × Hugging Face OpenEnv Hackathon** hosted by Scaler School of Technology (SST).

---

## 🚀 Overview

**Enterprise Workflow OpenEnv** simulates a realistic enterprise procurement pipeline where AI agents must complete multi-step workflows — from parsing purchase requisitions to drafting purchase orders and flagging approvals.

This environment is designed to benchmark and train agents on **structured decision-making** in real-world business contexts.

---

## 🧩 Tasks

| Difficulty | Description | Max Steps | Reward Range |
|------------|-------------|-----------|--------------|
| 🟢 **Easy** | Parse purchase requisition → match correct inventory item | 1 | 0.0 – 1.0 |
| 🟡 **Medium** | Parse requisition → check inventory → draft purchase order | 3 | 0.0 – 1.0 |
| 🔴 **Hard** | Full pipeline: parse → inventory → supplier → PO → approval | 5 | 0.0 – 1.0 |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/reset` | Reset the environment for a given task |
| `POST` | `/step` | Execute an agent action and get observation |
| `GET` | `/state/{task_id}` | Get the current state for a task |
| `GET` | `/tasks` | List all available tasks with schemas |
| `GET` | `/grader` | Run all graders and return scores |
| `GET` | `/baseline` | Return baseline scores for comparison |

---

## ⚡ Quick Start

### Reset Environment
```bash
curl -X POST https://MA4KU2-enterprise-workflow-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'
```

### Execute a Step
```bash
curl -X POST https://MA4KU2-enterprise-workflow-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy", "action_type": "parse_requisition", "payload": {"req_id": "REQ-001", "item_id": "ITEM-42"}}'
```

### Check Grader Scores
```bash
curl https://MA4KU2-enterprise-workflow-env.hf.space/grader
```

---

## 🏗️ Project Structure

```
├── server/
│   └── app.py          # FastAPI server entry point
├── app/
│   ├── main.py         # FastAPI app & route definitions
│   ├── environment.py  # WorkflowEnvironment logic
│   ├── models.py       # Pydantic models
│   ├── grader.py       # Grading logic
│   └── mock_backend.py # Mock enterprise backend
├── agent/
│   ├── baseline.py     # Baseline agent
│   └── tools.py        # Agent tools
├── tasks/
│   ├── easy.py         # Easy task definition
│   ├── medium.py       # Medium task definition
│   └── hard.py         # Hard task definition
├── openenv.yaml        # OpenEnv configuration
└── inference.py        # Inference entry point
```

---

## 🛠️ Built With

- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance API framework
- **[PyTorch](https://pytorch.org/)** — Meta's deep learning framework
- **[Hugging Face Spaces](https://huggingface.co/spaces)** — Deployment platform
- **[OpenEnv](https://openenv.dev/)** — Environment standard for AI agent training
- **Docker** — Containerized deployment

---

## 🏆 Hackathon

This project was submitted to the **Meta PyTorch OpenEnv Hackathon**, hosted by:
- 🏫 [Scaler School of Technology (SST)](https://www.scaler.com/school-of-technology/)
- 🤗 [Hugging Face](https://huggingface.co/)
- 🔥 [PyTorch](https://pytorch.org/)
- 🌐 [Meta](https://ai.meta.com/)

---

## 📄 License

MIT License — feel free to use and build upon this environment.

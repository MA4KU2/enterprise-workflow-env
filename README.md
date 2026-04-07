---
title: Enterprise Workflow OpenEnv
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Enterprise Workflow OpenEnv

A real-world OpenEnv environment for AI agent training on enterprise procurement workflows.

## Tasks
- **easy**: Parse requisition → match inventory item
- **medium**: 3-step workflow: parse → inventory → draft PO
- **hard**: 5-step pipeline: parse → inventory → supplier → PO → approval

## Endpoints
- `POST /reset` — reset environment
- `POST /step` — execute action
- `GET /state/{task_id}` — current state
- `GET /tasks` — list tasks
- `GET /grader` — run graders
- `GET /baseline` — baseline scores

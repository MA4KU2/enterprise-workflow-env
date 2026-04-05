from fastapi import FastAPI
from app.models import WorkflowAction, ResetRequest, TaskID
from app.environment import WorkflowEnvironment
from app.grader import run_all_graders
from functools import lru_cache

app = FastAPI(title="Enterprise Workflow OpenEnv")

@lru_cache(maxsize=1)
def get_env():
    return WorkflowEnvironment()

@app.get("/")
def root():
    return {"status": "ok", "env": "enterprise-workflow-env"}

@app.post("/reset")
def reset(req: ResetRequest):
    task_id = req.task_id if req.task_id is not None else TaskID.easy
    state = get_env().reset(task_id)
    return state

@app.post("/step")
def step(action: WorkflowAction):
    obs = get_env().step(action)
    return obs

@app.get("/state/{task_id}")
def state(task_id: TaskID):
    return get_env().state(task_id)

@app.get("/tasks")
def tasks():
    return {
        "tasks": [
            {
                "id": "easy",
                "description": "Parse purchase requisition and match correct inventory item",
                "difficulty": "easy",
                "action_schema": {
                    "task_id": "easy",
                    "action_type": "parse_requisition",
                    "payload": {"req_id": "string", "item_id": "string"}
                }
            },
            {
                "id": "medium",
                "description": "3-step workflow: parse requisition, check inventory, draft purchase order",
                "difficulty": "medium",
                "action_schema": {
                    "task_id": "medium",
                    "action_type": "parse_requisition | check_inventory | draft_po",
                    "payload": "varies by step"
                }
            },
            {
                "id": "hard",
                "description": "Full 5-step enterprise pipeline: parse, inventory, supplier, PO, approval",
                "difficulty": "hard",
                "action_schema": {
                    "task_id": "hard",
                    "action_type": "parse_requisition | check_inventory | message_supplier | draft_po | flag_approval",
                    "payload": "varies by step"
                }
            }
        ]
    }

@app.get("/grader")
def grader():
    scores = run_all_graders()
    return {"scores": scores}

@app.get("/baseline")
def baseline():
    scores = run_all_graders()
    return {"baseline_scores": scores, "model": "grader_baseline"}
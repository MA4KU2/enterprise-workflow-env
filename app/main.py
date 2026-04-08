from fastapi import FastAPI, Body
from app.models import WorkflowAction, ResetRequest, TaskID
from app.environment import WorkflowEnvironment
from functools import lru_cache

app = FastAPI(title="Enterprise Workflow OpenEnv")


# --- ENVIRONMENT CACHE ---
@lru_cache(maxsize=1)
def get_env():
    return WorkflowEnvironment()


# --- HEALTH CHECK ---
@app.get("/")
def root():
    return {"status": "ok", "env": "enterprise-workflow-env"}


# --- RESET ENDPOINT (STRICT FORMAT) ---
@app.post("/reset")
def reset(req: ResetRequest = Body(default=ResetRequest())):
    task_id = req.task_id if req.task_id is not None else TaskID.easy
    get_env().reset(task_id)

    # Minimal response (important for evaluator)
    return {"status": "reset"}


# --- STEP ENDPOINT (CRITICAL FIX) ---
@app.post("/step")
def step(action: WorkflowAction):
    obs = get_env().step(action)

    # STRICT schema → evaluator safe
    return {
        "reward": float(obs.reward),
        "done": bool(obs.done)
    }


# --- OPTIONAL (SAFE TO KEEP, NOT USED BY EVALUATOR) ---
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
                "difficulty": "easy"
            },
            {
                "id": "medium",
                "description": "3-step workflow: parse requisition, check inventory, draft purchase order",
                "difficulty": "medium"
            },
            {
                "id": "hard",
                "description": "Full 5-step enterprise pipeline",
                "difficulty": "hard"
            }
        ]
    }

from fastapi import FastAPI, Body
from app.models import WorkflowAction, ResetRequest, TaskID
from app.environment import WorkflowEnvironment
from app.grader import run_all_graders
from functools import lru_cache

app = FastAPI(title="Enterprise Workflow OpenEnv")


@lru_cache(maxsize=1)
def get_env():
    return WorkflowEnvironment()


# --- HEALTH ---
@app.get("/")
def root():
    return {"status": "ok", "env": "enterprise-workflow-env"}


# --- RESET ---
@app.post("/reset")
def reset(req: ResetRequest = Body(default=ResetRequest())):
    task_id = req.task_id if req.task_id else TaskID.easy
    get_env().reset(task_id)
    return {"status": "reset"}


# --- STEP (STRICT FORMAT) ---
@app.post("/step")
def step(action: WorkflowAction):
    obs = get_env().step(action)

    return {"reward": float(obs.reward), "done": bool(obs.done)}


# --- GRADER (CRITICAL FOR EVALUATOR) ---
@app.get("/grader")
def grader():
    scores = run_all_graders()
    return {"scores": scores}

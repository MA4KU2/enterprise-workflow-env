from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class TaskID(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class WorkflowAction(BaseModel):
    task_id: TaskID
    action_type: str  # "parse_requisition" | "check_inventory" | "draft_po" | "message_supplier" | "flag_approval"
    payload: Dict[str, Any] = {}

class WorkflowObservation(BaseModel):
    task_id: TaskID
    step: int
    result: Dict[str, Any]
    reward: float
    done: bool
    info: str = ""

class WorkflowState(BaseModel):
    task_id: TaskID
    step: int
    history: List[Dict[str, Any]] = []
    completed: bool = False
    total_reward: float = 0.0

class ResetRequest(BaseModel):
    task_id: TaskID

class ResetResponse(BaseModel):
    task_id: TaskID
    state: WorkflowState
    message: str = "Environment reset successfully"
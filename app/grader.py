from app.environment import WorkflowEnvironment
from app.models import TaskID, WorkflowAction

env = WorkflowEnvironment()

def grade_easy() -> float:
    env.reset(TaskID.easy)
    obs = env.step(WorkflowAction(
        task_id=TaskID.easy,
        action_type="parse_requisition",
        payload={"req_id": "REQ-001", "item_id": "ITM-001"}
    ))
    return round(obs.reward, 4)

def grade_medium() -> float:
    env.reset(TaskID.medium)
    obs1 = env.step(WorkflowAction(
        task_id=TaskID.medium,
        action_type="parse_requisition",
        payload={"req_id": "REQ-002"}
    ))
    obs2 = env.step(WorkflowAction(
        task_id=TaskID.medium,
        action_type="check_inventory",
        payload={"item_id": "ITM-002"}
    ))
    obs3 = env.step(WorkflowAction(
        task_id=TaskID.medium,
        action_type="draft_po",
        payload={"item_id": "ITM-002", "quantity": 10, "total_cost": 350.0, "department": "Operations"}
    ))
    return round(obs1.reward + obs2.reward + obs3.reward, 4)

def grade_hard() -> float:
    env.reset(TaskID.hard)
    obs1 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="parse_requisition",
        payload={"req_id": "REQ-003"}
    ))
    obs2 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="check_inventory",
        payload={"item_id": "ITM-003"}
    ))
    obs3 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="message_supplier",
        payload={"item_id": "ITM-003"}
    ))
    obs4 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="draft_po",
        payload={"item_id": "ITM-003", "quantity": 2, "total_cost": 900.0, "department": "HR"}
    ))
    obs5 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="flag_approval",
        payload={"approver": "cfo@company.com"}
    ))
    return round(obs1.reward + obs2.reward + obs3.reward + obs4.reward + obs5.reward, 4)

def run_all_graders() -> dict:
    return {
        "easy": grade_easy(),
        "medium": grade_medium(),
        "hard": grade_hard()
    }

if __name__ == "__main__":
    scores = run_all_graders()
    print(scores)
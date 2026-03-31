from app.environment import WorkflowEnvironment
from app.models import TaskID, WorkflowAction


def get_fresh_env():
    return WorkflowEnvironment()


# --- Core Safety Layer ---
def safe_score(x: float) -> float:
    """
    Ensures score is strictly within (0, 1)
    """
    if x <= 0:
        return 0.01
    elif x >= 1:
        return 0.99
    return round(x, 4)


# --- EASY TASK ---
def grade_easy() -> float:
    env = get_fresh_env()
    env.reset(TaskID.easy)

    obs = env.step(WorkflowAction(
        task_id=TaskID.easy,
        action_type="parse_requisition",
        payload={"req_id": "REQ-001", "item_id": "ITM-001"}
    ))

    return safe_score(obs.reward)


# --- MEDIUM TASK ---
def grade_medium() -> float:
    env = get_fresh_env()
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
        payload={
            "item_id": "ITM-002",
            "quantity": 10,
            "total_cost": 350.0,
            "department": "Operations"
        }
    ))

    total = obs1.reward + obs2.reward + obs3.reward

    # Option 1: Safe sum (keeps your logic)
    return safe_score(total)

    # Option 2 (recommended for stability):
    # return safe_score(total / 3)


# --- HARD TASK ---
def grade_hard() -> float:
    env = get_fresh_env()
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
        payload={
            "item_id": "ITM-003",
            "quantity": 2,
            "total_cost": 900.0,
            "department": "HR"
        }
    ))

    obs5 = env.step(WorkflowAction(
        task_id=TaskID.hard,
        action_type="flag_approval",
        payload={"approver": "cfo@company.com"}
    ))

    total = obs1.reward + obs2.reward + obs3.reward + obs4.reward + obs5.reward

    # Option 1: Safe sum
    return safe_score(total)

    # Option 2 (recommended for stability):
    # return safe_score(total / 5)


# --- RUNNER ---
def run_all_graders() -> dict:
    return {
        "easy": grade_easy(),
        "medium": grade_medium(),
        "hard": grade_hard()
    }


if __name__ == "__main__":
    scores = run_all_graders()
    print(scores)

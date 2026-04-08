from app.environment import WorkflowEnvironment
from app.models import TaskID, WorkflowAction
import math


def get_fresh_env():
    return WorkflowEnvironment()


# --- NORMALIZE AND CLAMP ---
def normalize_score(x: float, steps: int) -> float:
    """
    Normalize by expected total reward (always 1.0)
    then apply sigmoid
    """
    ratio = x / 1.0  # total expected reward is always 1.0
    sigmoid = 1 / (1 + math.exp(-5 * (ratio - 0.5)))
    return max(0.1, min(0.9, float(sigmoid)))


# --- EASY TASK ---
def grade_easy() -> float:
    env = get_fresh_env()
    env.reset(TaskID.easy)

    obs = env.step(
        WorkflowAction(
            task_id=TaskID.easy,
            action_type="parse_requisition",
            payload={"req_id": "REQ-001", "item_id": "ITM-001"},
        )
    )

    return normalize_score(obs.reward, 1)


# --- MEDIUM TASK ---
def grade_medium() -> float:
    env = get_fresh_env()
    env.reset(TaskID.medium)

    obs1 = env.step(
        WorkflowAction(
            task_id=TaskID.medium,
            action_type="parse_requisition",
            payload={"req_id": "REQ-002"},
        )
    )

    obs2 = env.step(
        WorkflowAction(
            task_id=TaskID.medium,
            action_type="check_inventory",
            payload={"item_id": "ITM-002"},
        )
    )

    obs3 = env.step(
        WorkflowAction(
            task_id=TaskID.medium,
            action_type="draft_po",
            payload={
                "item_id": "ITM-002",
                "quantity": 10,
                "total_cost": 350.0,
                "department": "Operations",
            },
        )
    )

    total = obs1.reward + obs2.reward + obs3.reward
    return normalize_score(total, 3)


# --- HARD TASK ---
def grade_hard() -> float:
    env = get_fresh_env()
    env.reset(TaskID.hard)

    obs1 = env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="parse_requisition",
            payload={"req_id": "REQ-003"},
        )
    )

    obs2 = env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="check_inventory",
            payload={"item_id": "ITM-003"},
        )
    )

    obs3 = env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="message_supplier",
            payload={"item_id": "ITM-003"},
        )
    )

    obs4 = env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="draft_po",
            payload={
                "item_id": "ITM-003",
                "quantity": 2,
                "total_cost": 900.0,
                "department": "HR",
            },
        )
    )

    obs5 = env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="flag_approval",
            payload={"approver": "cfo@company.com"},
        )
    )

    total = obs1.reward + obs2.reward + obs3.reward + obs4.reward + obs5.reward
    return normalize_score(total, 5)


# --- RUNNER ---
def run_all_graders() -> dict:
    return {"easy": grade_easy(), "medium": grade_medium(), "hard": grade_hard()}


if __name__ == "__main__":
    print(run_all_graders())

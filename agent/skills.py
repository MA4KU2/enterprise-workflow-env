"""
Enterprise Workflow Skills System
Adapted from Hermes Agent skill pattern (NousResearch/hermes-agent)
Provides reusable, composable workflow action definitions for smarter agent tool selection.
"""

from typing import List, Dict, Any, Optional


# --- SKILL DEFINITIONS ---
WORKFLOW_SKILLS = {
    "parse_requisition": {
        "description": "Parse a purchase requisition and extract item details",
        "action_type": "parse_requisition",
        "required_payload": ["req_id"],
        "optional_payload": ["item_id"],
        "applicable_tasks": ["easy", "medium", "hard"],
        "step": 0,
    },
    "check_inventory": {
        "description": "Check inventory availability for a given item",
        "action_type": "check_inventory",
        "required_payload": ["item_id"],
        "optional_payload": [],
        "applicable_tasks": ["medium", "hard"],
        "step": 1,
    },
    "message_supplier": {
        "description": "Contact supplier for an item not in inventory",
        "action_type": "message_supplier",
        "required_payload": ["item_id"],
        "optional_payload": [],
        "applicable_tasks": ["hard"],
        "step": 2,
    },
    "draft_po": {
        "description": "Draft a purchase order for approved items",
        "action_type": "draft_po",
        "required_payload": ["item_id", "quantity", "total_cost", "department"],
        "optional_payload": [],
        "applicable_tasks": ["medium", "hard"],
        "step": 3,
    },
    "flag_approval": {
        "description": "Flag purchase order for CFO/management approval",
        "action_type": "flag_approval",
        "required_payload": ["approver"],
        "optional_payload": [],
        "applicable_tasks": ["hard"],
        "step": 4,
    },
}

# --- TASK SKILL CHAINS ---
TASK_SKILL_CHAINS = {
    "easy": ["parse_requisition"],
    "medium": ["parse_requisition", "check_inventory", "draft_po"],
    "hard": [
        "parse_requisition",
        "check_inventory",
        "message_supplier",
        "draft_po",
        "flag_approval",
    ],
}

# --- MEMORY: remember past workflow decisions ---
_workflow_memory: List[Dict[str, Any]] = []


def remember(task_id: str, skill: str, payload: Dict, reward: float):
    """Store a workflow decision in memory."""
    _workflow_memory.append(
        {
            "task_id": task_id,
            "skill": skill,
            "payload": payload,
            "reward": reward,
        }
    )


def recall(task_id: str) -> List[Dict[str, Any]]:
    """Recall past decisions for a task."""
    return [m for m in _workflow_memory if m["task_id"] == task_id]


def recall_best(task_id: str, skill: str) -> Optional[Dict]:
    """Recall the best performing payload for a skill under a task."""
    past = [
        m for m in _workflow_memory if m["task_id"] == task_id and m["skill"] == skill
    ]
    if not past:
        return None
    return max(past, key=lambda x: x["reward"])


# --- SKILL RESOLUTION ---
def get_skill(name: str) -> Optional[Dict[str, Any]]:
    """Get a skill definition by name."""
    return WORKFLOW_SKILLS.get(name)


def get_task_skills(task_id: str) -> List[Dict[str, Any]]:
    """Get ordered skill chain for a task."""
    chain = TASK_SKILL_CHAINS.get(task_id, [])
    return [WORKFLOW_SKILLS[s] for s in chain if s in WORKFLOW_SKILLS]


def resolve_action(task_id: str, step: int) -> Optional[Dict[str, Any]]:
    """Resolve the correct skill for a given task and step."""
    chain = TASK_SKILL_CHAINS.get(task_id, [])
    if step < len(chain):
        return WORKFLOW_SKILLS.get(chain[step])
    return None


def validate_payload(skill_name: str, payload: Dict) -> List[str]:
    """Validate payload has all required fields. Returns list of missing fields."""
    skill = WORKFLOW_SKILLS.get(skill_name)
    if not skill:
        return [f"Unknown skill: {skill_name}"]
    return [f for f in skill["required_payload"] if f not in payload]


def get_all_skills() -> Dict[str, Any]:
    """Return all skill definitions."""
    return WORKFLOW_SKILLS


if __name__ == "__main__":
    print("Enterprise Workflow Skills System")
    print("=" * 50)
    for task, chain in TASK_SKILL_CHAINS.items():
        print(f"\n{task.upper()} task chain:")
        for skill_name in chain:
            skill = WORKFLOW_SKILLS[skill_name]
            print(f"  → {skill_name}: {skill['description']}")

import requests
import os

BASE_URL = os.getenv("ENV_URL", "https://ma4ku2-enterprise-workflow-env.hf.space")

def run_baseline():
    scores = {}

    # Easy
    requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})
    r = requests.post(f"{BASE_URL}/step", json={
        "task_id": "easy",
        "action_type": "parse_requisition",
        "payload": {"req_id": "REQ-001", "item_id": "ITM-001"}
    })
    scores["easy"] = r.json().get("reward", 0.0)

    # Medium
    requests.post(f"{BASE_URL}/reset", json={"task_id": "medium"})
    r1 = requests.post(f"{BASE_URL}/step", json={"task_id": "medium", "action_type": "parse_requisition", "payload": {"req_id": "REQ-002"}})
    r2 = requests.post(f"{BASE_URL}/step", json={"task_id": "medium", "action_type": "check_inventory", "payload": {"item_id": "ITM-002"}})
    r3 = requests.post(f"{BASE_URL}/step", json={"task_id": "medium", "action_type": "draft_po", "payload": {"item_id": "ITM-002", "quantity": 10, "total_cost": 350.0, "department": "Operations"}})
    scores["medium"] = round(r1.json().get("reward",0) + r2.json().get("reward",0) + r3.json().get("reward",0), 4)

    # Hard
    requests.post(f"{BASE_URL}/reset", json={"task_id": "hard"})
    h1 = requests.post(f"{BASE_URL}/step", json={"task_id": "hard", "action_type": "parse_requisition", "payload": {"req_id": "REQ-003"}})
    h2 = requests.post(f"{BASE_URL}/step", json={"task_id": "hard", "action_type": "check_inventory", "payload": {"item_id": "ITM-003"}})
    h3 = requests.post(f"{BASE_URL}/step", json={"task_id": "hard", "action_type": "message_supplier", "payload": {"item_id": "ITM-003"}})
    h4 = requests.post(f"{BASE_URL}/step", json={"task_id": "hard", "action_type": "draft_po", "payload": {"item_id": "ITM-003", "quantity": 2, "total_cost": 900.0, "department": "HR"}})
    h5 = requests.post(f"{BASE_URL}/step", json={"task_id": "hard", "action_type": "flag_approval", "payload": {"approver": "cfo@company.com"}})
    scores["hard"] = round(sum(x.json().get("reward",0) for x in [h1,h2,h3,h4,h5]), 4)

    print("Baseline scores:", scores)
    return scores

if __name__ == "__main__":
    run_baseline()
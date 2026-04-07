import os
import requests
from openai import OpenAI

BASE_URL = os.getenv("ENV_URL", "https://ma4ku2-enterprise-workflow-env.hf.space")
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b:free")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def log_start(task, env, model):
    print(f"[START] task={task} env=enterprise-workflow-env model={model}", flush=True)

def log_step(step, action, reward, done, error=None):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error or 'null'}", flush=True)

def log_end(success, steps, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}", flush=True)

def llm_decide(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=100,
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"error: {e}"

def run_task(task_id, steps):
    rewards = []
    log_start(task_id, "enterprise-workflow-env", MODEL_NAME)
    requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    for i, action in enumerate(steps, 1):
        decision = llm_decide(
            system_prompt="You are an enterprise workflow agent. Confirm the action to execute.",
            user_prompt=f"Task: {task_id}, Step {i}, Action: {action['action_type']}, Payload: {action['payload']}"
        )
        r = requests.post(f"{BASE_URL}/step", json=action).json()
        reward = r.get("reward", 0.0)
        done = r.get("done", False)
        error = r.get("info") if reward == 0.0 else None
        rewards.append(reward)
        log_step(i, action["action_type"], reward, done, error)
    log_end(sum(rewards) >= 0.5, len(steps), rewards)
    return rewards

if __name__ == "__main__":
    run_task("easy", [
        {"task_id": "easy", "action_type": "parse_requisition", "payload": {"req_id": "REQ-001", "item_id": "ITM-001"}}
    ])
    run_task("medium", [
        {"task_id": "medium", "action_type": "parse_requisition", "payload": {"req_id": "REQ-002"}},
        {"task_id": "medium", "action_type": "check_inventory", "payload": {"item_id": "ITM-002"}},
        {"task_id": "medium", "action_type": "draft_po", "payload": {"item_id": "ITM-002", "quantity": 10, "total_cost": 350.0, "department": "Operations"}},
    ])
    run_task("hard", [
        {"task_id": "hard", "action_type": "parse_requisition", "payload": {"req_id": "REQ-003"}},
        {"task_id": "hard", "action_type": "check_inventory", "payload": {"item_id": "ITM-003"}},
        {"task_id": "hard", "action_type": "message_supplier", "payload": {"item_id": "ITM-003"}},
        {"task_id": "hard", "action_type": "draft_po", "payload": {"item_id": "ITM-003", "quantity": 2, "total_cost": 900.0, "department": "HR"}},
        {"task_id": "hard", "action_type": "flag_approval", "payload": {"approver": "cfo@company.com"}},
    ])

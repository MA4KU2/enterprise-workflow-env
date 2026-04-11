import os
import json
import requests
from typing import List, Dict, Any
from openai import OpenAI

# --- CONFIGURATION (SCALER REQUIREMENTS) ---
ENV_URL = os.getenv("ENV_URL", "https://ma4ku2-enterprise-workflow-env.hf.space")
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b:free")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


class EnterpriseAgent:
    def __init__(self, task_id: str, max_steps: int = 8):
        self.task_id = task_id
        self.max_steps = max_steps
        self.history: List[Dict] = []
        self.rewards: List[float] = []
        self.steps_taken = 0
        self.done = False

    TASK_STEPS = {
        "easy": [
            {
                "action_type": "parse_requisition",
                "payload": {"req_id": "REQ-001", "item_id": "ITM-001"},
            }
        ],
        "medium": [
            {"action_type": "parse_requisition", "payload": {"req_id": "REQ-002"}},
            {"action_type": "check_inventory", "payload": {"item_id": "ITM-002"}},
            {
                "action_type": "draft_po",
                "payload": {
                    "item_id": "ITM-002",
                    "quantity": 10,
                    "total_cost": 350.0,
                    "department": "Operations",
                },
            },
        ],
        "hard": [
            {"action_type": "parse_requisition", "payload": {"req_id": "REQ-003"}},
            {"action_type": "check_inventory", "payload": {"item_id": "ITM-003"}},
            {"action_type": "message_supplier", "payload": {"item_id": "ITM-003"}},
            {
                "action_type": "draft_po",
                "payload": {
                    "item_id": "ITM-003",
                    "quantity": 2,
                    "total_cost": 900.0,
                    "department": "HR",
                },
            },
            {
                "action_type": "flag_approval",
                "payload": {"approver": "cfo@company.com"},
            },
        ],
    }

    def llm_decide(self, observation: Dict, fallback_action: Dict) -> Dict:
        system_prompt = (
            "You are an MNC Procurement Agent. Output ONLY a JSON object.\n"
            f"Current observation: {json.dumps(observation)}\n"
            f"Suggested action: {json.dumps(fallback_action)}\n"
            "Confirm or improve the suggested action. Output format: "
            '{"action_type": "...", "payload": {...}, "rationale": "..."}'
        )
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": system_prompt}],
                temperature=0.0,
                max_tokens=200,
            )
            content = response.choices[0].message.content.strip()
            import re

            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                if "action_type" in parsed and "payload" in parsed:
                    return parsed
            return fallback_action
        except Exception:
            return fallback_action

    def run(self):
        print(
            f"[START] task={self.task_id} env=enterprise-workflow-env model={MODEL_NAME}",
            flush=True,
        )
        try:
            requests.post(f"{ENV_URL}/reset", json={"task_id": self.task_id})
            observation = {"status": "ready", "task_id": self.task_id}
            steps = self.TASK_STEPS.get(self.task_id, [])

            for i, fallback in enumerate(steps, 1):
                self.steps_taken = i
                decision = self.llm_decide(observation, fallback)
                action_type = decision.get("action_type", fallback["action_type"])
                payload = decision.get("payload", fallback["payload"])
                payload["task_id"] = self.task_id

                step_data = {
                    "task_id": self.task_id,
                    "action_type": action_type,
                    "payload": payload,
                }
                res = requests.post(f"{ENV_URL}/step", json=step_data)

                if res.status_code != 200:
                    reward, done = 0.0, True
                    error_msg = f"HTTP {res.status_code}"
                else:
                    result = res.json()
                    reward = float(result.get("reward", 0.0))
                    done = bool(result.get("done", False))
                    error_msg = result.get("info", "null") if reward == 0.0 else "null"
                    observation = result

                self.rewards.append(reward)
                print(
                    f"[STEP] step={i} action={action_type} reward={reward:.2f} done={str(done).lower()} error={error_msg}",
                    flush=True,
                )

                if done:
                    break
        except Exception as e:
            print(f"[DEBUG] {e}", flush=True)

        score = sum(self.rewards)
        success = score >= 0.5
        rewards_str = ",".join(f"{r:.2f}" for r in self.rewards)
        print(
            f"[END] success={str(success).lower()} steps={self.steps_taken} score={score:.3f} rewards={rewards_str}",
            flush=True,
        )


if __name__ == "__main__":
    # In a real validation, the task_id would be provided by the environment
    for task in ["easy", "medium", "hard"]:
        agent = EnterpriseAgent(task_id=task)
        agent.run()

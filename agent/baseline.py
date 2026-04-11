import requests
import os
import json
from openai import OpenAI
from statistics import mean

BASE_URL = os.getenv("ENV_URL", "https://ma4ku2-enterprise-workflow-env.hf.space")
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b:free")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

# ---------------------------------------------------------------------------
# LLM-powered smart agent
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an enterprise procurement workflow AI agent.
Your job is to decide the next best action in a procurement pipeline.

You will receive the current task, step number, and available context.
Respond ONLY with a valid JSON object in this exact format:
{
  "action_type": "<action_type>",
  "payload": { <key>: <value> }
}

Action types per task:
- easy:   parse_requisition (payload: req_id, item_id)
- medium: parse_requisition (payload: req_id) → check_inventory (payload: item_id) → draft_po (payload: item_id, quantity, total_cost, department)
- hard:   parse_requisition → check_inventory → message_supplier (payload: item_id) → draft_po → flag_approval (payload: approver)

Be precise. Only output JSON, no explanation."""


def llm_action(task_id: str, step: int, context: dict) -> dict:
    """Ask the LLM to decide the next action given current context."""
    user_prompt = (
        f"Task: {task_id}\n"
        f"Step: {step}\n"
        f"Context: {json.dumps(context, indent=2)}\n\n"
        "What is the next action? Respond with JSON only."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  [LLM ERROR] {e} — using fallback", flush=True)
        return None


def clamp(score: float) -> float:
    return round(max(0.001, min(0.999, score)), 4)


# ---------------------------------------------------------------------------
# Fallback hardcoded actions (used when LLM fails)
# ---------------------------------------------------------------------------

FALLBACK_ACTIONS = {
    "easy": [
        {"action_type": "parse_requisition", "payload": {"req_id": "REQ-001", "item_id": "ITM-001"}},
    ],
    "medium": [
        {"action_type": "parse_requisition", "payload": {"req_id": "REQ-002"}},
        {"action_type": "check_inventory", "payload": {"item_id": "ITM-002"}},
        {"action_type": "draft_po", "payload": {"item_id": "ITM-002", "quantity": 10, "total_cost": 350.0, "department": "Operations"}},
    ],
    "hard": [
        {"action_type": "parse_requisition", "payload": {"req_id": "REQ-003"}},
        {"action_type": "check_inventory", "payload": {"item_id": "ITM-003"}},
        {"action_type": "message_supplier", "payload": {"item_id": "ITM-003"}},
        {"action_type": "draft_po", "payload": {"item_id": "ITM-003", "quantity": 2, "total_cost": 900.0, "department": "HR"}},
        {"action_type": "flag_approval", "payload": {"approver": "cfo@company.com"}},
    ],
}

# Context seeds per task for LLM guidance
CONTEXT_SEEDS = {
    "easy":   {"req_id": "REQ-001", "hint": "Match item_id ITM-001 to the laptop requisition"},
    "medium": {"req_id": "REQ-002", "item_id": "ITM-002", "quantity": 10, "total_cost": 350.0, "department": "Operations"},
    "hard":   {"req_id": "REQ-003", "item_id": "ITM-003", "quantity": 2, "total_cost": 900.0, "department": "HR", "approver": "cfo@company.com"},
}


# ---------------------------------------------------------------------------
# Single episode runner
# ---------------------------------------------------------------------------

def run_episode(task_id: str, episode: int = 1, use_llm: bool = True) -> dict:
    """Run one episode of a task. Returns episode result dict."""
    print(f"\n  [Episode {episode}] task={task_id} mode={'llm' if use_llm else 'fallback'}", flush=True)

    requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})

    fallback_steps = FALLBACK_ACTIONS[task_id]
    context = CONTEXT_SEEDS[task_id].copy()
    rewards = []
    success = False

    for step_idx, fallback in enumerate(fallback_steps):
        # Try LLM first, fall back to hardcoded if it fails
        action = None
        if use_llm:
            action = llm_action(task_id, step_idx + 1, context)

        if action is None:
            action = fallback

        full_action = {"task_id": task_id, **action}
        resp = requests.post(f"{BASE_URL}/step", json=full_action).json()

        reward = resp.get("reward", 0.0)
        done = resp.get("done", False)
        info = resp.get("info", "")

        rewards.append(reward)
        context["last_result"] = resp.get("result", {})
        context["last_info"] = info

        print(f"    step={step_idx+1} action={action['action_type']} reward={reward:.4f} done={done} info={info}", flush=True)

        if done:
            success = reward > 0
            break

    raw_score = sum(rewards)
    score = clamp(raw_score)
    print(f"  [Episode {episode} END] score={score} rewards={[round(r,4) for r in rewards]}", flush=True)

    return {"episode": episode, "score": score, "rewards": rewards, "success": success}


# ---------------------------------------------------------------------------
# Multi-episode runner
# ---------------------------------------------------------------------------

def run_multi_episode(task_id: str, n_episodes: int = 3, use_llm: bool = True) -> dict:
    """Run multiple episodes and aggregate stats."""
    print(f"\n{'='*55}", flush=True)
    print(f"TASK: {task_id.upper()} — {n_episodes} episodes", flush=True)
    print(f"{'='*55}", flush=True)

    results = []
    for ep in range(1, n_episodes + 1):
        result = run_episode(task_id, episode=ep, use_llm=use_llm)
        results.append(result)

    scores = [r["score"] for r in results]
    successes = [r["success"] for r in results]

    summary = {
        "task_id": task_id,
        "n_episodes": n_episodes,
        "scores": scores,
        "mean_score": clamp(mean(scores)),
        "max_score": clamp(max(scores)),
        "min_score": clamp(min(scores)),
        "success_rate": round(sum(successes) / n_episodes, 4),
    }

    print(f"\n  [{task_id.upper()} SUMMARY]", flush=True)
    print(f"  mean={summary['mean_score']} max={summary['max_score']} min={summary['min_score']} success_rate={summary['success_rate']}", flush=True)

    return summary


# ---------------------------------------------------------------------------
# Main baseline
# ---------------------------------------------------------------------------

def run_baseline(n_episodes: int = 3, use_llm: bool = True) -> dict:
    """Run full baseline across all tasks with multi-episode support."""
    print(f"\n{'#'*55}", flush=True)
    print(f"  ENTERPRISE WORKFLOW BASELINE", flush=True)
    print(f"  episodes={n_episodes}  llm={'enabled' if use_llm else 'disabled'}", flush=True)
    print(f"{'#'*55}", flush=True)

    all_results = {}
    for task_id in ["easy", "medium", "hard"]:
        summary = run_multi_episode(task_id, n_episodes=n_episodes, use_llm=use_llm)
        all_results[task_id] = summary

    # Final report
    print(f"\n{'#'*55}", flush=True)
    print("  FINAL BASELINE SCORES", flush=True)
    print(f"{'#'*55}", flush=True)
    for task_id, summary in all_results.items():
        print(
            f"  {task_id:8s} mean={summary['mean_score']:.4f}  "
            f"max={summary['max_score']:.4f}  "
            f"success_rate={summary['success_rate']:.2%}",
            flush=True,
        )

    return all_results


if __name__ == "__main__":
    # Run 3 episodes per task with LLM agent
    # Set use_llm=False to run pure fallback (deterministic)
    run_baseline(n_episodes=3, use_llm=True)

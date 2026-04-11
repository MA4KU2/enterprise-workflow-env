"""Trajectory Compressor
Adapted from NousResearch/hermes-agent trajectory_compressor.py
Compresses completed episode history to fit within token budget
while preserving training signal quality.
"""

import math
from typing import List, Dict, Any, Tuple


def count_tokens_approx(text: str) -> int:
    """Approximate token count (4 chars per token)."""
    return max(1, len(text) // 4)


def count_trajectory_tokens(trajectory: List[Dict]) -> int:
    """Count total approximate tokens in a trajectory."""
    return sum(count_tokens_approx(str(t)) for t in trajectory)


def compress_trajectory(
    trajectory: List[Dict],
    target_max_tokens: int = 2000,
    protect_last_n: int = 2,
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Compress a trajectory to fit within token budget.

    Strategy:
    1. Protect first and last N steps
    2. Summarize middle steps if over budget
    3. Return compressed trajectory + metrics

    Args:
        trajectory: List of step dicts with action/result/reward
        target_max_tokens: Max token budget
        protect_last_n: Number of recent steps to always keep

    Returns:
        (compressed_trajectory, metrics_dict)
    """
    original_tokens = count_trajectory_tokens(trajectory)
    original_len = len(trajectory)

    metrics = {
        "original_steps": original_len,
        "original_tokens": original_tokens,
        "compressed": False,
        "tokens_saved": 0,
        "steps_removed": 0,
    }

    # No compression needed
    if original_tokens <= target_max_tokens or original_len <= protect_last_n + 1:
        metrics["compressed_steps"] = original_len
        metrics["compressed_tokens"] = original_tokens
        return trajectory, metrics

    # Protect head (first step) and tail (last N steps)
    head = trajectory[:1]
    tail = trajectory[-protect_last_n:]
    middle = trajectory[1:-protect_last_n]

    if not middle:
        metrics["compressed_steps"] = original_len
        metrics["compressed_tokens"] = original_tokens
        return trajectory, metrics

    # Summarize middle steps
    summary_parts = []
    for i, step in enumerate(middle):
        action = step.get("action", {})
        reward = step.get("reward", 0.0)
        action_type = (
            action.get("action_type", "unknown")
            if isinstance(action, dict)
            else str(action)
        )
        summary_parts.append(f"Step {i + 1}: {action_type} → reward={reward:.2f}")

    summary_step = {
        "action": {"action_type": "context_summary"},
        "result": {"summary": " | ".join(summary_parts)},
        "reward": sum(s.get("reward", 0) for s in middle),
        "info": f"[COMPRESSED: {len(middle)} steps summarized]",
    }

    compressed = head + [summary_step] + tail
    compressed_tokens = count_trajectory_tokens(compressed)

    metrics["compressed"] = True
    metrics["compressed_steps"] = len(compressed)
    metrics["compressed_tokens"] = compressed_tokens
    metrics["tokens_saved"] = original_tokens - compressed_tokens
    metrics["steps_removed"] = original_len - len(compressed)

    return compressed, metrics


def maybe_compress(
    history: List[Dict],
    target_max_tokens: int = 2000,
) -> Tuple[List[Dict], bool]:
    """
    Compress history only if over token budget.
    Returns (history, was_compressed).
    """
    if count_trajectory_tokens(history) <= target_max_tokens:
        return history, False
    compressed, metrics = compress_trajectory(history, target_max_tokens)
    if metrics["compressed"]:
        print(
            f"[COMPRESS] {metrics['original_steps']} steps → "
            f"{metrics['compressed_steps']} steps | "
            f"saved {metrics['tokens_saved']} tokens",
            flush=True,
        )
    return compressed, metrics["compressed"]

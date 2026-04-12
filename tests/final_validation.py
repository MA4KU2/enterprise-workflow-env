#!/usr/bin/env python3
"""
Final validation showing that the refactored system works correctly.
This tests the core logic without requiring LLM API calls.
"""

import os
import sys

# Set dummy credentials to avoid auth errors but allow imports
os.environ["HF_TOKEN"] = "dummy-validation-token"
os.environ["API_KEY"] = "dummy-validation-key"

sys.path.insert(0, ".")


def test_environment_logic():
    """Test that our refactored environment logic is correct"""
    print("🔍 Testing Refactored Environment Logic")
    print("=" * 50)

    from app.environment import WorkflowEnvironment
    from app.models import TaskID, WorkflowAction

    # Test 1: Easy task - should work with correct sequence
    print("\n📝 Test 1: Easy Task (parse_requisition only)")
    env = WorkflowEnvironment()
    env.reset(TaskID.easy)

    action = WorkflowAction(
        task_id=TaskID.easy,
        action_type="parse_requisition",
        payload={"req_id": "REQ-001", "item_id": "ITM-001"},
    )
    obs = env.step(action)
    print(f"   Reward: {obs.reward:.2f}, Done: {obs.done}")
    print(f"   Expected: ~0.99 reward, done=true")
    assert obs.reward > 0.9 and obs.done, "Easy task should succeed"
    print("   ✅ PASS")

    # Test 2: Medium task - should work with correct sequence
    print("\n📝 Test 2: Medium Task (parse → check_inventory → draft_po)")
    env = WorkflowEnvironment()
    env.reset(TaskID.medium)

    # Step 1: parse_requisition
    action1 = WorkflowAction(
        task_id=TaskID.medium,
        action_type="parse_requisition",
        payload={"req_id": "REQ-002"},
    )
    obs1 = env.step(action1)
    print(f"   Step 1 (parse): Reward: {obs1.reward:.2f}, Done: {obs1.done}")
    assert obs1.reward > 0.3 and not obs1.done, "Should get ~0.33 reward, not done"

    # Step 2: check_inventory
    action2 = WorkflowAction(
        task_id=TaskID.medium,
        action_type="check_inventory",
        payload={"item_id": "ITM-002"},
    )
    obs2 = env.step(action2)
    print(f"   Step 2 (check_inventory): Reward: {obs2.reward:.2f}, Done: {obs2.done}")
    assert obs2.reward > 0.3 and not obs2.done, "Should get ~0.33 reward, not done"

    # Step 3: draft_po (with correct financial validation)
    action3 = WorkflowAction(
        task_id=TaskID.medium,
        action_type="draft_po",
        payload={
            "item_id": "ITM-002",
            "quantity": 10,
            "total_cost": 350.0,  # 10 * 35.00 (unit price from mock_backend)
            "department": "Operations",
        },
    )
    obs3 = env.step(action3)
    print(f"   Step 3 (draft_po): Reward: {obs3.reward:.2f}, Done: {obs3.done}")
    assert obs3.reward > 0.3 and obs3.done, "Should get ~0.33 reward, done=true"

    total_medium = obs1.reward + obs2.reward + obs3.reward
    print(f"   Total Medium Reward: {total_medium:.2f} (expected ~0.99)")
    assert total_medium > 0.9, "Medium task should succeed"
    print("   ✅ PASS")

    # Test 3: Financial Guardrails - should fail with incorrect math
    print("\n💰 Test 3: Financial Guardrails (Incorrect total_cost)")
    env = WorkflowEnvironment()
    env.reset(TaskID.medium)

    # Do first two steps
    env.step(
        WorkflowAction(
            task_id=TaskID.medium,
            action_type="parse_requisition",
            payload={"req_id": "REQ-002"},
        )
    )
    env.step(
        WorkflowAction(
            task_id=TaskID.medium,
            action_type="check_inventory",
            payload={"item_id": "ITM-002"},
        )
    )

    # Try draft_po with WRONG total_cost
    action_wrong = WorkflowAction(
        task_id=TaskID.medium,
        action_type="draft_po",
        payload={
            "item_id": "ITM-002",
            "quantity": 10,
            "total_cost": 500.0,  # WRONG! Should be 350.0 (10 * 35.00)
            "department": "Operations",
        },
    )
    obs_wrong = env.step(action_wrong)
    print(f"   Incorrect PO: Reward: {obs_wrong.reward:.2f}, Done: {obs_wrong.done}")
    print(f"   Info: {obs_wrong.info}")
    assert obs_wrong.reward == 0.0 and obs_wrong.done, (
        "Should fail financial validation"
    )
    assert "Financial validation failed" in obs_wrong.info, (
        "Should mention financial validation"
    )
    print("   ✅ PASS - Correctly blocked invalid PO")

    # Test 4: Reward Shaping - should get penalty for premature message_supplier
    print("\n⚖️ Test 4: Reward Shaping (Premature message_supplier penalty)")
    env = WorkflowEnvironment()
    env.reset(TaskID.hard)

    # Step 1: parse_requisition (required first)
    env.step(
        WorkflowAction(
            task_id=TaskID.hard,
            action_type="parse_requisition",
            payload={"req_id": "REQ-003"},
        )
    )

    # Step 2: Try message_supplier BEFORE check_inventory (should get penalty)
    action_premature = WorkflowAction(
        task_id=TaskID.hard,
        action_type="message_supplier",
        payload={"item_id": "ITM-003"},
    )
    obs_penalty = env.step(action_premature)
    print(
        f"   Premature message_supplier: Reward: {obs_penalty.reward:.2f}, Done: {obs_penalty.done}"
    )
    print(f"   Info: {obs_penalty.info}")
    assert obs_penalty.reward == 0.0 and not obs_penalty.done, (
        "Should get 0.0 penalty via prerequisite gate"
    )
    assert "Prerequisite not met" in obs_penalty.info, "Should mention prerequisite"
    print("   ✅ PASS - Correctly blocked by prerequisite gate")

    # Test 5: Hard task with correct sequence should work
    print("\n📝 Test 5: Hard Task (Full correct sequence)")
    env = WorkflowEnvironment()
    env.reset(TaskID.hard)

    steps = [
        ("parse_requisition", {"req_id": "REQ-003"}),
        ("check_inventory", {"item_id": "ITM-003"}),
        ("message_supplier", {"item_id": "ITM-003"}),
        (
            "draft_po",
            {
                "item_id": "ITM-003",
                "quantity": 2,
                "total_cost": 900.0,  # 2 * 450.00 (ITM-003 unit price)
                "department": "HR",
            },
        ),
        ("flag_approval", {"approver": "cfo@company.com"}),
    ]

    total_reward = 0.0
    for i, (action_type, payload) in enumerate(steps, 1):
        action = WorkflowAction(
            task_id=TaskID.hard, action_type=action_type, payload=payload
        )
        obs = env.step(action)
        total_reward += obs.reward
        print(
            f"   Step {i} ({action_type}): Reward: {obs.reward:.2f}, Done: {obs.done}"
        )
        if not obs.done and i < len(steps):
            assert obs.reward > 0, f"Step {i} should give positive reward"

    print(f"   Total Hard Reward: {total_reward:.2f} (expected ~0.99)")
    assert total_reward > 0.9 and obs.done, "Hard task should succeed"
    print("   ✅ PASS")

    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Refactored environment logic is working correctly")
    print("✅ State-dependent actions functioning")
    print("✅ Financial guardrails active")
    print("✅ Reward shaping implemented")
    print("✅ System ready for LLM integration")
    return True


if __name__ == "__main__":
    test_environment_logic()

from app.models import TaskID, WorkflowAction, WorkflowObservation, WorkflowState
from app.mock_backend import (
    get_inventory,
    get_requisition,
    get_supplier,
    match_item_from_description,
)
from typing import Dict


class WorkflowEnvironment:
    def __init__(self):
        self.sessions: Dict[str, WorkflowState] = {}
        self.prerequisites = {
            "draft_po": ["check_inventory"],
            "message_supplier": ["check_inventory"],
            "flag_approval": ["draft_po"],
        }

    def reset(self, task_id: TaskID) -> WorkflowState:
        state = WorkflowState(
            task_id=task_id, step=0, history=[], completed=False, total_reward=0.0
        )
        self.sessions[task_id.value] = state
        return state

    def step(self, action: WorkflowAction) -> WorkflowObservation:
        task_id = action.task_id
        state = self.sessions.get(task_id.value)
        if state is None:
            state = self.reset(task_id)

        reward = 0.0
        done = False
        result = {}
        info = ""

        # Check prerequisites
        if action.action_type in self.prerequisites:
            required_actions = self.prerequisites[action.action_type]
            if not all(
                req in [a["action"]["action_type"] for a in state.history]
                for req in required_actions
            ):
                return WorkflowObservation(
                    task_id=task_id,
                    step=state.step,
                    result={},
                    reward=0.0,
                    done=False,
                    info=f"Prerequisite not met: {', '.join(required_actions)}",
                )

        # Execute action based on task type
        if task_id == TaskID.easy:
            reward, done, result, info = self._run_easy(action, state)
        elif task_id == TaskID.medium:
            reward, done, result, info = self._run_medium(action, state)
        elif task_id == TaskID.hard:
            reward, done, result, info = self._run_hard(action, state)

        state.step += 1
        state.total_reward += reward
        state.history.append(
            {"action": action.dict(), "result": result, "reward": reward}
        )
        if done:
            state.completed = True

        return WorkflowObservation(
            task_id=task_id,
            step=state.step,
            result=result,
            reward=reward,
            done=done,
            info=info,
        )

    def state(self, task_id: TaskID) -> WorkflowState:
        return self.sessions.get(task_id.value, self.reset(task_id))

    def _run_easy(self, action, state):
        req_id = action.payload.get("req_id", "REQ-001")
        req = get_requisition(req_id)
        if not req:
            return 0.0, True, {}, "Invalid requisition ID"
        matched = action.payload.get("item_id", "")
        correct = req.get("expected_item_id", "")
        if matched == correct:
            return 0.99, True, {"matched_item": get_inventory(matched)}, "Correct match"
        elif matched in ["ITM-001", "ITM-002", "ITM-003", "ITM-004", "ITM-005"]:
            return (
                0.3,
                True,
                {"matched_item": get_inventory(matched)},
                "Wrong item matched",
            )
        return 0.0, True, {}, "No valid item provided"

    def _run_medium(self, action, state):
        step = state.step
        # Step 0: parse_requisition
        if step == 0:
            if action.action_type != "parse_requisition":
                return 0.0, False, {}, "Expected parse_requisition first"
            req_id = action.payload.get("req_id", "REQ-001")
            req = get_requisition(req_id)
            if not req:
                return 0.0, True, {}, "Invalid requisition"
            item_id = match_item_from_description(req.get("description", ""))
            # Store item_id in history for later steps
            state.history.append(
                {"item_id": item_id, "req": req, "action": action.dict()}
            )
            return (
                0.33,
                False,
                {"requisition": req, "suggested_item": item_id},
                "Step 1 complete",
            )
        # Step 1: check_inventory (Bug‑fixed block)
        elif step == 1:
            if action.action_type != "check_inventory":
                return 0.0, False, {}, "Expected check_inventory"
            item_id = action.payload.get("item_id", "")
            if not item_id:
                return 0.0, False, {}, "Item not found"
            inv = get_inventory(item_id)
            if not inv:
                return 0.0, False, {}, "Item not found"
            return 0.33, False, {"inventory": inv}, "Step 2 complete"
        # Step 2: draft_po (includes unknown‑item and financial guardrails)
        elif step == 2:
            if action.action_type != "draft_po":
                return 0.0, True, {}, "Expected draft_po"
            # Ensure we have the item ID from the payload
            item_id = action.payload.get("item_id", "")
            if not any(
                a["action"]["action_type"] == "check_inventory" for a in state.history
            ):
                return 0.0, False, {}, "Expected check_inventory first"
            required = ["item_id", "quantity", "total_cost", "department"]
            missing = [f for f in required if f not in action.payload]
            if missing:
                return 0.1, True, {"missing_fields": missing}, "Incomplete PO"
            # Handle unknown items gracefully
            item_id = action.payload.get("item_id", "")
            if not item_id:
                return 0.0, True, {}, "Item not found in description - flag for review"
            # Financial Guardrails (Sprint A)
            quantity = action.payload.get("quantity", 0)
            total_cost = action.payload.get("total_cost", 0.0)
            if item_id and quantity > 0:
                inventory_item = get_inventory(item_id)
                if inventory_item:
                    unit_price = inventory_item.get("unit_price", 0.0)
                    expected_cost = quantity * unit_price
                    if abs(total_cost - expected_cost) > 0.01:
                        return (
                            0.0,
                            True,
                            {},
                            f"Financial validation failed: expected {expected_cost}, got {total_cost}",
                        )
            return 0.33, True, {"po_draft": action.payload}, "PO drafted successfully"
        else:
            return 0.0, False, {}, "Unexpected action type"

    def _run_hard(self, action, state):
        # Check if parse_requisition has been completed
        if action.action_type == "check_inventory":
            if not any(
                a["action"]["action_type"] == "parse_requisition" for a in state.history
            ):
                return 0.0, False, {}, "Expected parse_requisition first"
            inv = get_inventory(action.payload.get("item_id", ""))
            if not inv:
                return 0.0, False, {}, "Item not found"
            return 0.2, False, {"inventory": inv}, "Inventory checked"

        # Check if check_inventory has been completed before message_supplier
        elif action.action_type == "message_supplier":
            # Reward Shaping (Sprint B): Negative reward if message_supplier before check_inventory
            if not any(
                a["action"]["action_type"] == "check_inventory" for a in state.history
            ):
                return (
                    -0.5,
                    False,
                    {},
                    "Penalty: message_supplier before check_inventory",
                )
            supplier = get_supplier(action.payload.get("item_id", ""))
            if not supplier:
                return 0.0, False, {}, "Supplier not found"
            return 0.2, False, {"supplier_contacted": supplier}, "Supplier contacted"

        # Check if message_supplier has been completed before draft_po
        elif action.action_type == "draft_po":
            if not any(
                a["action"]["action_type"] == "check_inventory" for a in state.history
            ):
                return 0.0, False, {}, "Expected check_inventory first"
            required = ["item_id", "quantity", "total_cost", "department"]
            missing = [f for f in required if f not in action.payload]
            if missing:
                return 0.1, False, {"missing_fields": missing}, "Incomplete PO"

            # Handle unknown items gracefully
            item_id = action.payload.get("item_id", "")
            if not item_id:
                return 0.0, True, {}, "Item not found in description - flag for review"

            # Financial Guardrails (Sprint A): Validate total_cost == quantity * unit_price
            quantity = action.payload.get("quantity", 0)
            total_cost = action.payload.get("total_cost", 0.0)

            if item_id and quantity > 0:
                inventory_item = get_inventory(item_id)
                if inventory_item:
                    unit_price = inventory_item.get("unit_price", 0.0)
                    expected_cost = quantity * unit_price
                    if (
                        abs(total_cost - expected_cost) > 0.01
                    ):  # Allow small floating point differences
                        return (
                            0.0,
                            True,
                            {},
                            f"Financial validation failed: expected {expected_cost}, got {total_cost}",
                        )

            return 0.2, False, {"po_draft": action.payload}, "PO drafted"

        # Check if draft_po has been completed before flag_approval
        elif action.action_type == "flag_approval":
            if not any(a["action"]["action_type"] == "draft_po" for a in state.history):
                return 0.0, False, {}, "Expected draft_po first"
            approver = action.payload.get("approver", "")
            if approver:
                return 0.19, True, {"flagged_to": approver}, "Full pipeline complete"
            return 0.1, True, {}, "Missing approver"

        # Handle parse_requisition as first step
        elif action.action_type == "parse_requisition":
            req = get_requisition(action.payload.get("req_id", "REQ-001"))
            item_id = match_item_from_description(req.get("description", ""))
            return (
                0.2,
                False,
                {"requisition": req, "suggested_item": item_id},
                "Requisition parsed",
            )

        return 0.0, False, {}, "Unexpected action type"

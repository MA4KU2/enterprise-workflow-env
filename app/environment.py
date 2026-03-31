from app.models import TaskID, WorkflowAction, WorkflowObservation, WorkflowState
from app.mock_backend import get_inventory, get_requisition, get_supplier, match_item_from_description
from typing import Dict

class WorkflowEnvironment:
    def __init__(self):
        self.sessions: Dict[str, WorkflowState] = {}

    def reset(self, task_id: TaskID) -> WorkflowState:
        state = WorkflowState(task_id=task_id, step=0, history=[], completed=False, total_reward=0.0)
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

        if task_id == TaskID.easy:
            reward, done, result, info = self._run_easy(action, state)
        elif task_id == TaskID.medium:
            reward, done, result, info = self._run_medium(action, state)
        elif task_id == TaskID.hard:
            reward, done, result, info = self._run_hard(action, state)

        state.step += 1
        state.total_reward += reward
        state.history.append({"action": action.dict(), "result": result, "reward": reward})
        if done:
            state.completed = True

        return WorkflowObservation(
            task_id=task_id, step=state.step,
            result=result, reward=reward, done=done, info=info
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
            return 1.0, True, {"matched_item": get_inventory(matched)}, "Correct match"
        elif matched in ["ITM-001","ITM-002","ITM-003","ITM-004","ITM-005"]:
            return 0.3, True, {"matched_item": get_inventory(matched)}, "Wrong item matched"
        return 0.0, True, {}, "No valid item provided"

    def _run_medium(self, action, state):
        step = state.step
        if step == 0:
            if action.action_type != "parse_requisition":
                return 0.0, False, {}, "Expected parse_requisition first"
            req_id = action.payload.get("req_id", "REQ-001")
            req = get_requisition(req_id)
            if not req:
                return 0.0, True, {}, "Invalid requisition"
            item_id = match_item_from_description(req["description"])
            state.history.append({"item_id": item_id, "req": req})
            return 0.33, False, {"requisition": req, "suggested_item": item_id}, "Step 1 complete"
        elif step == 1:
            if action.action_type != "check_inventory":
                return 0.0, False, {}, "Expected check_inventory"
            item_id = action.payload.get("item_id", "")
            inv = get_inventory(item_id)
            if not inv:
                return 0.0, False, {}, "Item not found"
            return 0.33, False, {"inventory": inv}, "Step 2 complete"
        elif step == 2:
            if action.action_type != "draft_po":
                return 0.0, True, {}, "Expected draft_po"
            required = ["item_id", "quantity", "total_cost", "department"]
            missing = [f for f in required if f not in action.payload]
            if missing:
                return 0.1, True, {"missing_fields": missing}, "Incomplete PO"
            return 0.34, True, {"po_draft": action.payload}, "PO drafted successfully"
        return 0.0, True, {}, "Unexpected step"

    def _run_hard(self, action, state):
        step = state.step
        if step == 0:
            if action.action_type != "parse_requisition":
                return 0.0, False, {}, "Expected parse_requisition"
            req = get_requisition(action.payload.get("req_id", "REQ-001"))
            item_id = match_item_from_description(req.get("description",""))
            return 0.2, False, {"requisition": req, "suggested_item": item_id}, "Step 1 done"
        elif step == 1:
            if action.action_type != "check_inventory":
                return 0.0, False, {}, "Expected check_inventory"
            inv = get_inventory(action.payload.get("item_id",""))
            return 0.2, False, {"inventory": inv}, "Step 2 done"
        elif step == 2:
            if action.action_type != "message_supplier":
                return 0.0, False, {}, "Expected message_supplier"
            supplier = get_supplier(action.payload.get("item_id",""))
            if not supplier:
                return 0.0, False, {}, "Supplier not found"
            return 0.2, False, {"supplier_contacted": supplier}, "Step 3 done"
        elif step == 3:
            if action.action_type != "draft_po":
                return 0.0, False, {}, "Expected draft_po"
            required = ["item_id","quantity","total_cost","department"]
            missing = [f for f in required if f not in action.payload]
            if missing:
                return 0.1, False, {"missing_fields": missing}, "Incomplete PO"
            return 0.2, False, {"po_draft": action.payload}, "Step 4 done"
        elif step == 4:
            if action.action_type != "flag_approval":
                return 0.0, True, {}, "Expected flag_approval"
            approver = action.payload.get("approver","")
            if approver:
                return 0.2, True, {"flagged_to": approver}, "Full pipeline complete"
            return 0.1, True, {}, "Missing approver"
        return 0.0, True, {}, "Unexpected step"
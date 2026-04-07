INVENTORY = {
    "ITM-001": {"name": "Laptop Dell XPS 15", "stock": 12, "unit_price": 1200.00},
    "ITM-002": {"name": "USB-C Hub 7-port", "stock": 45, "unit_price": 35.00},
    "ITM-003": {"name": "Standing Desk Electric", "stock": 5, "unit_price": 450.00},
    "ITM-004": {"name": "Mechanical Keyboard", "stock": 30, "unit_price": 85.00},
    "ITM-005": {"name": "4K Monitor 27inch", "stock": 8, "unit_price": 380.00},
}

REQUISITIONS = {
    "REQ-001": {
        "description": "Need 3 units of portable laptop for new hires",
        "department": "Engineering",
        "budget": 4000.00,
        "urgency": "high",
        "expected_item_id": "ITM-001"
    },
    "REQ-002": {
        "description": "Require 10 USB hubs for conference room setup",
        "department": "Operations",
        "budget": 500.00,
        "urgency": "medium",
        "expected_item_id": "ITM-002"
    },
    "REQ-003": {
        "description": "Purchase 2 adjustable standing desks for ergonomics program",
        "department": "HR",
        "budget": 1000.00,
        "urgency": "low",
        "expected_item_id": "ITM-003"
    },
}

SUPPLIERS = {
    "ITM-001": {"name": "TechDirect Ltd", "email": "orders@techdirect.com", "lead_days": 5},
    "ITM-002": {"name": "OfficeGear Co", "email": "supply@officegear.com", "lead_days": 2},
    "ITM-003": {"name": "ErgoFurniture Inc", "email": "bulk@ergofurniture.com", "lead_days": 10},
    "ITM-004": {"name": "PeriphHub", "email": "orders@periphub.com", "lead_days": 3},
    "ITM-005": {"name": "DisplayPro", "email": "sales@displaypro.com", "lead_days": 7},
}

def get_inventory(item_id: str) -> dict:
    return INVENTORY.get(item_id, {})

def get_requisition(req_id: str) -> dict:
    return REQUISITIONS.get(req_id, {})

def get_supplier(item_id: str) -> dict:
    return SUPPLIERS.get(item_id, {})

def match_item_from_description(description: str) -> str:
    description = description.lower()
    if "laptop" in description:
        return "ITM-001"
    elif "usb" in description or "hub" in description:
        return "ITM-002"
    elif "desk" in description or "standing" in description:
        return "ITM-003"
    elif "keyboard" in description:
        return "ITM-004"
    elif "monitor" in description or "display" in description:
        return "ITM-005"
    return ""
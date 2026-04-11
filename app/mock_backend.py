INVENTORY = {
    # Original items
    "ITM-001": {
        "name": "Laptop Dell XPS 15",
        "stock": 12,
        "unit_price": 1200.00,
        "category": "computing",
    },
    "ITM-002": {
        "name": "USB-C Hub 7-port",
        "stock": 45,
        "unit_price": 35.00,
        "category": "accessories",
    },
    "ITM-003": {
        "name": "Standing Desk Electric",
        "stock": 5,
        "unit_price": 450.00,
        "category": "furniture",
    },
    "ITM-004": {
        "name": "Mechanical Keyboard",
        "stock": 30,
        "unit_price": 85.00,
        "category": "accessories",
    },
    "ITM-005": {
        "name": "4K Monitor 27inch",
        "stock": 8,
        "unit_price": 380.00,
        "category": "displays",
    },
    # New items
    "ITM-006": {
        "name": "MacBook Pro 14inch",
        "stock": 6,
        "unit_price": 1999.00,
        "category": "computing",
    },
    "ITM-007": {
        "name": "Ergonomic Office Chair",
        "stock": 15,
        "unit_price": 320.00,
        "category": "furniture",
    },
    "ITM-008": {
        "name": "Wireless Mouse Logitech MX",
        "stock": 60,
        "unit_price": 45.00,
        "category": "accessories",
    },
    "ITM-009": {
        "name": "Noise Cancelling Headphones",
        "stock": 20,
        "unit_price": 250.00,
        "category": "audio",
    },
    "ITM-010": {
        "name": "Webcam 4K Pro",
        "stock": 25,
        "unit_price": 120.00,
        "category": "peripherals",
    },
    "ITM-011": {
        "name": "Docking Station Thunderbolt",
        "stock": 18,
        "unit_price": 180.00,
        "category": "accessories",
    },
    "ITM-012": {
        "name": "External SSD 2TB",
        "stock": 35,
        "unit_price": 140.00,
        "category": "storage",
    },
    "ITM-013": {
        "name": "iPad Pro 12.9inch",
        "stock": 10,
        "unit_price": 1099.00,
        "category": "computing",
    },
    "ITM-014": {
        "name": "Whiteboard 6ft",
        "stock": 7,
        "unit_price": 95.00,
        "category": "office",
    },
    "ITM-015": {
        "name": "Conference Speakerphone",
        "stock": 12,
        "unit_price": 210.00,
        "category": "audio",
    },
}

REQUISITIONS = {
    # Original requisitions
    "REQ-001": {
        "description": "Need 3 units of portable laptop for new hires",
        "department": "Engineering",
        "budget": 4000.00,
        "urgency": "high",
        "expected_item_id": "ITM-001",
    },
    "REQ-002": {
        "description": "Require 10 USB hubs for conference room setup",
        "department": "Operations",
        "budget": 500.00,
        "urgency": "medium",
        "expected_item_id": "ITM-002",
    },
    "REQ-003": {
        "description": "Purchase 2 adjustable standing desks for ergonomics program",
        "department": "HR",
        "budget": 1000.00,
        "urgency": "low",
        "expected_item_id": "ITM-003",
    },
    # New requisitions
    "REQ-004": {
        "description": "Request 5 MacBook Pro laptops for design team",
        "department": "Design",
        "budget": 11000.00,
        "urgency": "high",
        "expected_item_id": "ITM-006",
    },
    "REQ-005": {
        "description": "Need 8 ergonomic chairs for new office floor",
        "department": "Facilities",
        "budget": 3000.00,
        "urgency": "medium",
        "expected_item_id": "ITM-007",
    },
    "REQ-006": {
        "description": "Order 20 wireless mice for remote work kits",
        "department": "IT",
        "budget": 1000.00,
        "urgency": "low",
        "expected_item_id": "ITM-008",
    },
    "REQ-007": {
        "description": "Purchase 10 noise cancelling headphones for call center",
        "department": "Support",
        "budget": 2800.00,
        "urgency": "high",
        "expected_item_id": "ITM-009",
    },
    "REQ-008": {
        "description": "Need 6 webcams for video conferencing rooms",
        "department": "Operations",
        "budget": 800.00,
        "urgency": "medium",
        "expected_item_id": "ITM-010",
    },
    "REQ-009": {
        "description": "Request 15 thunderbolt docking stations for hybrid workers",
        "department": "Engineering",
        "budget": 3000.00,
        "urgency": "medium",
        "expected_item_id": "ITM-011",
    },
    "REQ-010": {
        "description": "Require 4 external SSD drives for backup storage",
        "department": "IT",
        "budget": 600.00,
        "urgency": "low",
        "expected_item_id": "ITM-012",
    },
    "REQ-011": {
        "description": "Need 4 external SSD drives for backup storage",
        "department": "IT",
        "budget": 600.00,
        "urgency": "low",
        "expected_item_id": "ITM-012",
    },
    "REQ-012": {
        "description": "Purchase 6 webcams for video conferencing rooms",
        "department": "Operations",
        "budget": 800.00,
        "urgency": "medium",
        "expected_item_id": "ITM-010",
    },
    "REQ-013": {
        "description": "Request 15 thunderbolt docking stations for hybrid workers",
        "department": "Engineering",
        "budget": 3000.00,
        "urgency": "medium",
        "expected_item_id": "ITM-011",
    },
}

SUPPLIERS = {
    # Original suppliers
    "ITM-001": {
        "name": "TechDirect Ltd",
        "email": "orders@techdirect.com",
        "lead_days": 5,
        "rating": 4.8,
    },
    "ITM-002": {
        "name": "OfficeGear Co",
        "email": "supply@officegear.com",
        "lead_days": 2,
        "rating": 4.5,
    },
    "ITM-003": {
        "name": "ErgoFurniture Inc",
        "email": "bulk@ergofurniture.com",
        "lead_days": 10,
        "rating": 4.3,
    },
    "ITM-004": {
        "name": "PeriphHub",
        "email": "orders@periphub.com",
        "lead_days": 3,
        "rating": 4.6,
    },
    "ITM-005": {
        "name": "DisplayPro",
        "email": "sales@displaypro.com",
        "lead_days": 7,
        "rating": 4.7,
    },
    # New suppliers
    "ITM-006": {
        "name": "AppleBiz Solutions",
        "email": "enterprise@applebiz.com",
        "lead_days": 7,
        "rating": 4.9,
    },
    "ITM-007": {
        "name": "ErgoFurniture Inc",
        "email": "bulk@ergofurniture.com",
        "lead_days": 8,
        "rating": 4.3,
    },
    "ITM-008": {
        "name": "PeriphHub",
        "email": "orders@periphub.com",
        "lead_days": 2,
        "rating": 4.6,
    },
    "ITM-009": {
        "name": "SoundTech Enterprise",
        "email": "b2b@soundtech.com",
        "lead_days": 4,
        "rating": 4.7,
    },
    "ITM-010": {
        "name": "VisionGear Pro",
        "email": "orders@visiongear.com",
        "lead_days": 3,
        "rating": 4.4,
    },
    "ITM-011": {
        "name": "TechDirect Ltd",
        "email": "orders@techdirect.com",
        "lead_days": 5,
        "rating": 4.8,
    },
    "ITM-012": {
        "name": "StoragePlus Corp",
        "email": "sales@storageplus.com",
        "lead_days": 3,
        "rating": 4.5,
    },
    "ITM-013": {
        "name": "AppleBiz Solutions",
        "email": "enterprise@applebiz.com",
        "lead_days": 6,
        "rating": 4.9,
    },
    "ITM-014": {
        "name": "OfficeGear Co",
        "email": "supply@officegear.com",
        "lead_days": 3,
        "rating": 4.5,
    },
    "ITM-015": {
        "name": "SoundTech Enterprise",
        "email": "b2b@soundtech.com",
        "lead_days": 5,
        "rating": 4.7,
    },
}


def get_inventory(item_id: str) -> dict:
    return INVENTORY.get(item_id, {})


def get_requisition(req_id: str) -> dict:
    return REQUISITIONS.get(req_id, {})


def get_supplier(item_id: str) -> dict:
    return SUPPLIERS.get(item_id, {})


def list_requisitions() -> list:
    return list(REQUISITIONS.keys())


def list_inventory() -> list:
    return list(INVENTORY.keys())


def match_item_from_description(description: str) -> str:
    description = description.lower()
    if "macbook" in description or "apple" in description:
        return "ITM-006"
    elif "laptop" in description or "dell" in description:
        return "ITM-001"
    elif "ipad" in description or "tablet" in description:
        return "ITM-013"
    elif "usb" in description or "hub" in description:
        return "ITM-002"
    elif "docking" in description or "thunderbolt" in description:
        return "ITM-011"
    elif "standing desk" in description or "stand" in description:
        return "ITM-003"
    elif (
        "chair" in description or "ergonomic" in description and "chair" in description
    ):
        return "ITM-007"
    elif "whiteboard" in description:
        return "ITM-014"
    elif "keyboard" in description:
        return "ITM-004"
    elif "mouse" in description or "mice" in description:
        return "ITM-008"
    elif "headphone" in description or "noise cancel" in description:
        return "ITM-009"
    elif "speaker" in description or "speakerphone" in description:
        return "ITM-015"
    elif "webcam" in description or "camera" in description:
        return "ITM-010"
    elif "monitor" in description or "display" in description:
        return "ITM-005"
    elif "ssd" in description or "storage" in description or "drive" in description:
        return "ITM-012"
    return ""

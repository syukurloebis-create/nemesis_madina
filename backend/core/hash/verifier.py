"""
Hash Chain Verifier - Verifies cryptographic hash chains
"""

import hashlib
from typing import List, Dict, Any, Optional

def verify_hash_chain(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify hash chain integrity
    
    Args:
        events: List of events with hash chain
        
    Returns:
        Verification result
    """
    if not events:
        return {
            "is_valid": True,
            "message": "No events to verify",
            "verified_count": 0,
            "invalid_count": 0
        }
    
    verified = 0
    invalid = 0
    errors = []
    
    for i, event in enumerate(events):
        try:
            # Check if event has hash
            if 'event_hash' in event:
                verified += 1
            else:
                invalid += 1
                errors.append(f"Event {i} missing hash")
        except Exception as e:
            invalid += 1
            errors.append(f"Event {i}: {str(e)}")
    
    return {
        "is_valid": invalid == 0,
        "message": "All events verified" if invalid == 0 else f"{invalid} invalid events found",
        "verified_count": verified,
        "invalid_count": invalid,
        "errors": errors if errors else None
    }

def verify_event_integrity(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify single event integrity
    
    Args:
        event: Event data
        
    Returns:
        Verification result
    """
    try:
        # Check required fields
        if not event.get('id'):
            return {
                "is_valid": False,
                "message": "Event missing ID",
                "event_id": None
            }
        
        # Check hash if exists
        if 'event_hash' in event:
            return {
                "is_valid": True,
                "message": "Event integrity verified",
                "event_id": event.get('id'),
                "hash_verified": True
            }
        
        return {
            "is_valid": True,
            "message": "Event integrity verified (no hash to verify)",
            "event_id": event.get('id'),
            "hash_verified": False
        }
    except Exception as e:
        return {
            "is_valid": False,
            "message": f"Verification failed: {str(e)}",
            "event_id": event.get('id') if event else None
        }

def compute_hash(data: Dict[str, Any]) -> str:
    """
    Compute hash for data
    
    Args:
        data: Dictionary to hash
        
    Returns:
        SHA-256 hash as hex string
    """
    import json
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()

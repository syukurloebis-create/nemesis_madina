from backend.core.security.hash_verifier import (
    verify_chain
)

def test_valid_chain():

    events = [
        {
            "aggregate_id":"A",
            "sequence_num":1,
            "event_type":"created",
            "payload":{},
            "previous_hash":None,
            "event_hash":"..."
        }
    ]

    result = verify_chain(events)

    assert "verified" in result
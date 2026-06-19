# backend/events/verifier.py - Simplified version

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IntegrityVerifier:
    def __init__(self, repository):
        self.repository = repository
    
    async def verify_aggregate_chain(self, aggregate_id: str) -> Dict[str, Any]:
        """Verify event chain integrity for a case"""
        try:
            events = await self.repository.get_events(aggregate_id)
            
            if not events:
                return {
                    'status': 'EMPTY',
                    'events_verified': 0,
                    'message': 'No events found for this case'
                }
            
            failed_events = []
            previous_hash = None
            
            for i, event in enumerate(events):
                event_id = event.get('event_id')
                event_version = event.get('version')
                current_hash = event.get('event_hash')
                stored_previous = event.get('previous_hash')
                
                # Check 1: Event must have a hash
                if not current_hash:
                    failed_events.append({
                        'event_id': event_id,
                        'version': event_version,
                        'reason': 'missing_hash',
                        'message': 'Event hash is null'
                    })
                    continue
                
                # Check 2: Chain integrity - first event has no previous_hash
                if i == 0:
                    if stored_previous is not None:
                        failed_events.append({
                            'event_id': event_id,
                            'version': event_version,
                            'reason': 'first_event_has_previous',
                            'message': 'First event should not have previous_hash'
                        })
                else:
                    # Non-first events must have previous_hash that matches previous event's hash
                    if not stored_previous:
                        failed_events.append({
                            'event_id': event_id,
                            'version': event_version,
                            'reason': 'missing_previous_hash',
                            'message': f'Event version {event_version} missing previous_hash'
                        })
                    elif stored_previous != previous_hash:
                        failed_events.append({
                            'event_id': event_id,
                            'version': event_version,
                            'reason': 'chain_break',
                            'expected_previous': previous_hash,
                            'actual_previous': stored_previous
                        })
                
                # Update previous_hash for next iteration
                previous_hash = current_hash
            
            # Also verify the last event's chain
            if previous_hash and events[-1].get('previous_hash') != events[-2].get('event_hash') if len(events) > 1 else True:
                pass  # Already handled above
            
            return {
                'status': 'PASS' if not failed_events else 'FAIL',
                'events_verified': len(events),
                'chain_intact': len(failed_events) == 0,
                'failed_events': failed_events
            }
        
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return {
                'status': 'ERROR',
                'events_verified': 0,
                'chain_intact': False,
                'error': str(e)
            }
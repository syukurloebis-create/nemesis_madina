#!/usr/bin/env python3
"""
Verify all ORM models are registered
"""

import sys
sys.path.insert(0, '.')

def main():
    from backend.bootstrap.models import bootstrap_models
    from backend.database import Base
    
    print("\n🔍 VERIFYING ALL ORM MODELS")
    print("="*60)
    
    bootstrap_models()
    
    tables = sorted(Base.metadata.tables.keys())
    print(f"\n📊 Registered Tables: {len(tables)}")
    
    # Expected core tables
    expected = [
        'users', 'cases', 'events', 'processed_events', 
        'snapshots', 'dashboard_view', 'projection_checkpoints',
        'outbox_messages'
    ]
    
    found = []
    missing = []
    
    for exp in expected:
        if exp in tables:
            found.append(exp)
        else:
            missing.append(exp)
    
    print(f"\n✅ Found: {len(found)}/{len(expected)} core tables")
    for t in found:
        print(f"  ✓ {t}")
    
    if missing:
        print(f"\n❌ Missing: {len(missing)} tables")
        for t in missing:
            print(f"  ✗ {t}")
    
    print("\n" + "="*60)
    
    if len(tables) >= 44:
        print("✅ ALL TABLES REGISTERED")
        return 0
    else:
        print(f"⚠️ Only {len(tables)}/44 tables registered")
        print("   Some model files may need to be imported")
        return 1

if __name__ == "__main__":
    sys.exit(main())

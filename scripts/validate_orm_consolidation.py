#!/usr/bin/env python3
"""
Validate ORM consolidation - run AFTER changes
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Validate ORM consolidation."""
    print("\n🔍 Validating ORM Consolidation")
    print("="*60)
    
    try:
        # Bootstrap models
        from backend.bootstrap.models import bootstrap_models, get_registry_summary
        
        print("  Bootstrapping models...")
        bootstrap_models()
        
        summary = get_registry_summary()
        
        print(f"\n  ✅ Bootstrapped: {summary['bootstrapped']}")
        print(f"  📊 Tables: {summary['table_count']}")
        print(f"  📊 Mappers: {summary['mapper_count']}")
        
        if summary['table_count'] > 0:
            print(f"\n  Tables registered:")
            for table in summary['tables']:
                print(f"    - {table}")
            
            print(f"\n  ✅ Registry consolidation successful!")
            print(f"  ✅ {summary['table_count']} tables registered")
            return 0
        else:
            print(f"\n  ❌ No tables registered")
            print("  Check model imports in bootstrap_models()")
            return 1
            
    except Exception as e:
        print(f"\n  ❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())

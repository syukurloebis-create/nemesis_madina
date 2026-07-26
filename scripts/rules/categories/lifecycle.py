# scripts/rules/categories/lifecycle.py
class LifecycleRule:
    def __init__(self, capability_registry: IRegistry, inventory: IInventoryQuery):
        self.registry = capability_registry
        self.inventory = inventory
    
    def validate(self):
        violations = []
        capabilities = self.registry.list()
        
        for cap in capabilities:
            lifecycle = CapabilityLifecycle(cap.get('maturity'))
            
            # Check if capability is active
            if not CapabilityLifecycle.is_active(lifecycle):
                violations.append({
                    'rule_id': 'LIFECYCLE-001',
                    'message': f"Capability {cap['id']} is {lifecycle.value}",
                    'severity': 'high' if lifecycle == CapabilityLifecycle.REMOVED else 'medium',
                    'capability': cap['id']
                })
            
            # Check dependencies
            for dep in cap.get('depends_on', []):
                dep_cap = self.registry.get(dep)
                if dep_cap:
                    dep_lifecycle = CapabilityLifecycle(dep_cap.get('maturity'))
                    if not CapabilityLifecycle.can_depend_on(lifecycle, dep_lifecycle):
                        violations.append({
                            'rule_id': 'LIFECYCLE-002',
                            'message': f"Capability {cap['id']} depends on deprecated/removed: {dep}",
                            'severity': 'high',
                            'capability': cap['id'],
                            'dependency': dep
                        })
            
            # Check if production capability has tests
            if lifecycle == CapabilityLifecycle.PRODUCTION:
                for module in cap.get('modules', []):
                    if not self.inventory.has_tests(module):
                        violations.append({
                            'rule_id': 'LIFECYCLE-003',
                            'message': f"Production capability {cap['id']} missing tests for {module}",
                            'severity': 'high',
                            'capability': cap['id'],
                            'module': module
                        })
        
        return violations
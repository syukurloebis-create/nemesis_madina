# scripts/architecture/registries/factory.py
class RegistryFactory:
    """Factory for creating registries"""
    
    _registries = {}
    
    @classmethod
    def create(cls, registry_type: str, config: Dict[str, Any]) -> IRegistry:
        """Create a registry instance"""
        
        # Choose provider
        provider_type = config.get('provider', 'yaml')
        if provider_type == 'yaml':
            provider = YamlRegistryProvider(config['path'])
        elif provider_type == 'database':
            provider = DatabaseRegistryProvider(config['connection'])
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
        
        # Create registry
        if registry_type == 'capability':
            registry = CapabilityRegistry(provider)
        elif registry_type == 'adr':
            registry = ADRRegistry(provider)
        elif registry_type == 'domain':
            registry = DomainRegistry(provider)
        elif registry_type == 'event':
            registry = EventRegistry(provider)
        else:
            raise ValueError(f"Unknown registry type: {registry_type}")
        
        cls._registries[registry_type] = registry
        return registry
    
    @classmethod
    def get(cls, registry_type: str) -> Optional[IRegistry]:
        """Get existing registry instance"""
        return cls._registries.get(registry_type)
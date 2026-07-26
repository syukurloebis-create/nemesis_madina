# scripts/rules/categories/__init__.py
class RuleCategories:
    """Define rule category graph"""
    
    @classmethod
    def get_graph(cls) -> RuleGraph:
        """Build rule dependency graph"""
        graph = RuleGraph()
        
        # Define rules with dependencies
        graph.add_rule(RuleNode(
            id='architecture',
            name='Architecture Rules',
            category='architecture'
        ))
        
        graph.add_rule(RuleNode(
            id='ddd',
            name='DDD Rules',
            category='ddd',
            depends_on=['architecture']
        ))
        
        graph.add_rule(RuleNode(
            id='aggregate',
            name='Aggregate Rules',
            category='ddd',
            depends_on=['ddd']
        ))
        
        graph.add_rule(RuleNode(
            id='repository',
            name='Repository Rules',
            category='ddd',
            depends_on=['ddd']
        ))
        
        graph.add_rule(RuleNode(
            id='cqrs',
            name='CQRS Rules',
            category='cqrs',
            depends_on=['architecture']
        ))
        
        graph.add_rule(RuleNode(
            id='security',
            name='Security Rules',
            category='security',
            depends_on=['architecture']
        ))
        
        graph.add_rule(RuleNode(
            id='naming',
            name='Naming Rules',
            category='naming',
            depends_on=['architecture']
        ))
        
        graph.add_rule(RuleNode(
            id='performance',
            name='Performance Rules',
            category='performance',
            depends_on=['architecture']
        ))
        
        # Validate graph
        errors = graph.validate()
        if errors:
            raise ValueError(f"Rule graph validation failed: {errors}")
        
        return graph
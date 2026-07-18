"""
Graph SQL Compatibility Layer

Centralized place for all graph JOIN queries.
When graph_entities.id is migrated to UUID,
only this file needs to be changed.
"""

class GraphSQL:
    """
    Centralized graph SQL queries with compatibility layer.
    """
    
    # ============================================================
    # COMPATIBILITY JOINS (dengan CAST UUID)
    # ============================================================
    # TODO: Migrasi graph_entities.id dari VARCHAR ke UUID
    # Setelah migrasi selesai, ubah:
    #   ge.id::uuid → ge.id
    # ============================================================
    
    ENTITY_JOIN = """
        JOIN graph_entities ge
        ON ge.id::uuid = ns.entity_id
    """
    
    CLUSTER_JOIN = """
        JOIN graph_entities ge
        ON ge.id::uuid = gc.entity_id
    """
    
    # Query templates
    ENTITIES_COUNT = """
        SELECT COUNT(*) as entity_count
        FROM graph_entities
        WHERE case_id = :case_id
    """
    
    RELATIONSHIPS_COUNT = """
        SELECT COUNT(*) as rel_count
        FROM graph_relationships
        WHERE case_id = :case_id
    """
    
    CLUSTERS_COUNT = f"""
        SELECT COUNT(DISTINCT gc.cluster_id) as cluster_count
        FROM graph_clusters gc
        {CLUSTER_JOIN}
        WHERE ge.case_id = :case_id
    """
    
    PAGERANK_STATS = f"""
        SELECT 
            AVG(ns.pagerank) as avg_pagerank,
            MAX(ns.pagerank) as max_pagerank,
            COUNT(*) as node_count
        FROM graph_node_scores ns
        {ENTITY_JOIN}
        WHERE ge.case_id = :case_id
    """
    
    TOP_HUBS = f"""
        SELECT 
            ge.id as entity_id,
            ge.name,
            ns.pagerank
        FROM graph_node_scores ns
        {ENTITY_JOIN}
        WHERE ge.case_id = :case_id
        ORDER BY ns.pagerank DESC
        LIMIT 10
    """
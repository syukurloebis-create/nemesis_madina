def validate_graph(graph):
    issues = []

    for node in graph.nodes:

        # ❌ INVALID AMOUNT NODE DETECTION
        if node["type"] == "account" and len(node["name"]) > 10:
            issues.append("Invalid account node format")

        # ❌ PERSON NAME VALIDATION
        if node["type"] == "person" and node["name"].isdigit():
            issues.append("Numeric person node detected")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges)
    }
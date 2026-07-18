# \# ADR-031: Duplicate Handling Strategy

# 

# \## Status

# Approved

# 

# \## Context

# GraphBuilder may encounter duplicate nodes (same business\_key) 

# or duplicate edges during graph building.

# 

# \## Decision

# Two modes supported:

# 1\. \*\*REPAIR mode (default)\*\*: Duplicates are removed automatically.

# &#x20;  Statistics track how many duplicates were removed.

# &#x20;  Safe for production.

# 

# 2\. \*\*STRICT mode\*\*: Duplicates raise ValueError.

# &#x20;  Used for testing and validation.

# 

# \## Consequences

# \- REPAIR mode ensures graph building never fails due to duplicates.

# \- STRICT mode helps detect data quality issues.

# \- Statistics provide visibility into duplicate removal.


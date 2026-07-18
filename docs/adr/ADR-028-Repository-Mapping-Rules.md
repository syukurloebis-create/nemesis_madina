# \# ADR-028: Repository Mapping Rules

# 

# \*\*Status:\*\* APPROVED

# 

# \*\*Decision:\*\* Separate Mapper layer for Aggregate ↔ Model conversion.

# 

# \*\*Layers:\*\*

# 1\. Domain → Aggregate (pure domain)

# 2\. Application → Mapper (DTO ↔ Aggregate)

# 3\. Infrastructure → Model (SQLAlchemy)

# 4\. Infrastructure → Mapper (Aggregate ↔ Model)


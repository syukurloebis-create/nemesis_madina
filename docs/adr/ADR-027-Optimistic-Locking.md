# \# ADR-027: Optimistic Locking

# 

# \*\*Status:\*\* APPROVED

# 

# \*\*Decision:\*\* Aggregate has version field. Repository uses version for concurrency control.

# 

# \*\*Flow:\*\*

# 1\. Aggregate.\_version increments on every event

# 2\. Repository.load() → loads aggregate with version

# 3\. Repository.save() → checks WHERE version = expected\_version

# 4\. If version mismatch → DomainConflictError

# 5\. Application retries with fresh aggregate


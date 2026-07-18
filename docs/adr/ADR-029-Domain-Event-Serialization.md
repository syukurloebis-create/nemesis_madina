# \# ADR-029: Domain Event Serialization

# 

# \*\*Status:\*\* APPROVED

# 

# \*\*Decision:\*\* Domain events are serialized to JSON for Outbox.

# 

# \*\*Rules:\*\*

# 1\. Events are JSON-serializable

# 2\. Event name = class name

# 3\. Version field for schema evolution

# 4\. Infrastructure adds metadata on publishing


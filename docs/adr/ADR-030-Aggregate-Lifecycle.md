# \# ADR-030: Aggregate Lifecycle

# 

# \*\*Status:\*\* APPROVED

# 

# \*\*Decision:\*\* Standard lifecycle for all aggregates.

# 

# \*\*States:\*\*

# 1\. CREATE → Aggregate instantiated

# 2\. LOAD → Repository.load()

# 3\. MUTATE → apply business logic

# 4\. RECORD → events stored in \_pending\_events

# 5\. PERSIST → Repository.save()

# 6\. PUBLISH → UnitOfWork pulls and publishes events

# 7\. CLEAR → events cleared after publishing


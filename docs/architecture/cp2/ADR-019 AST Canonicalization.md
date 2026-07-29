# \# ADR-019: AST Canonicalization

# 

# \## Status

# \*\*ACCEPTED\*\* (2026-07-29)

# 

# \## Context

# CP1 established the IR foundation (models, allocators, hashing, repositories). CP2 needs to transform Python AST into canonical IR entities with deterministic behavior.

# 

# \## Decision

# AST Canonicalization SHALL be implemented with the following principles:

# 

# \### Scope

# \- Parse Python source code using `ast.parse`

# \- Traverse AST using visitor pattern

# \- Emit IR entities to repositories

# \- Normalize IR to canonical form

# \- Serialize to deterministic JSON

# 

# \### Non-Goals

# \- Semantic analysis (type inference, binding, resolution)

# \- Graph building (import graph, call graph)

# \- Architecture validation

# 

# \### Canonicalization Rules

# 1\. AST SHALL be traversed in deterministic order

# 2\. IR entities SHALL be emitted in stable order

# 3\. All IDs SHALL be allocated deterministically

# 4\. JSON output SHALL be canonical (sorted keys, UTF-8, LF newline)

# 

# \### Dependency Rules

# \- Parser → Visitor → Emitter → Repositories → Normalizer → Serializer

# \- No circular dependencies

# \- Serializer SHALL NOT import Visitor

# \- Visitor SHALL NOT import Serializer

# \- Normalizer SHALL NOT parse AST

# \- Parser SHALL NOT emit IR

# 

# \### Error Handling

# \- Syntax errors SHALL be captured as diagnostics

# \- Parser SHALL NOT crash on invalid syntax

# \- Invalid syntax SHALL NOT block other files

# 

# \### Future Compatibility

# \- Schema version SHALL be preserved in all artifacts

# \- Extension points SHALL be available for future features

# \- Golden regression SHALL catch breaking changes

# 

# \## Consequences

# \- AST is parsed exactly once

# \- IR is the single source of truth for downstream analysis

# \- All artifacts are deterministic and reproducible

# \- Changes to AST canonicalization require ADR update


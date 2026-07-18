# \# docs/architecture/implementation-guide.md

# 

# \# NEMESIS Architecture v8.1 - Implementation Guide

# 

# \## Overview

# 

# This guide documents the implementation of v8.1 baseline.

# 

# \## Components

# 

# \### Scanner

# \- Plugin-based architecture

# \- Python plugin implemented

# \- Incremental scanning with cache

# 

# \### Normalizer

# \- Validates raw data

# \- Converts to domain models

# \- Extracts relations

# 

# \### Inventory

# \- SQLite storage with versioning

# \- FTS5 search

# \- Query engine

# 

# \### Rule Engine

# \- Structural rules (forbidden imports, domain purity)

# \- Semantic rules (ADR, capability)

# \- Violation reporting

# 

# \### Generators

# \- Manifest generation

# \- Report generation

# \- Graph generation

# \- Dashboard data

# 

# \### CI/CD Gate

# \- Four levels: Informational → Warning → Soft Fail → Hard Fail

# \- GitHub Actions integration

# \- PR comments

# 

# \## Commands

# 

# ```bash

# \# Generate inventory

# nemesis generate-inventory

# 

# \# Evaluate rules

# nemesis evaluate-rules

# 

# \# Generate reports

# nemesis generate-reports

# 

# \# Evaluate gate

# nemesis gate --level soft\_fail

# 

# \# Full pipeline

# nemesis pipeline run


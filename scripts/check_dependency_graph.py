#!/usr/bin/env python3
"""
check_dependency_graph.py - ADR-030 Architecture Validation

Builds dependency graph from production entry points.
Allows Frozen → Frozen dependencies.
Disallows Entry Point → Frozen dependencies.
"""

import sys
from check_frozen_imports import main as check_imports

if __name__ == "__main__":
    sys.exit(check_imports())
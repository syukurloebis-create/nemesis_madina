# scripts/metadata_inventory/discovery/registry_discovery.py
"""
Registry Discovery - Runtime discovery with single GC iteration.
Phase 2 - Discovery Runtime (Revised)
"""

import gc
import sys
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

from .registry_identity import RegistryFingerprint
from .discovery_context import DiscoveryContext


class RegistryDiscovery:
    """
    Menemukan semua SQLAlchemy registry di runtime.
    Single GC iteration for efficiency.
    """
    
    def __init__(self, canonical_module: str = "backend.database", canonical_base: str = "Base"):
        self.canonical_module = canonical_module
        self.canonical_base = canonical_base
        self._canonical_context: Optional[DiscoveryContext] = None
        self._other_contexts: List[DiscoveryContext] = []
    
    def discover_all(self) -> Tuple[Optional[DiscoveryContext], List[DiscoveryContext]]:
        """
        Discover all registries.
        Returns: (canonical_context, other_contexts)
        """
        contexts = []
        
        # 1. Canonical Base (primary)
        canonical_context = self._discover_canonical()
        if canonical_context:
            contexts.append(canonical_context)
            self._canonical_context = canonical_context
        
        # 2. Single GC iteration for all other registries
        other_contexts = self._discover_from_gc(canonical_context)
        contexts.extend(other_contexts)
        self._other_contexts = other_contexts
        
        # 3. AST fallback (if no registries found)
        if not contexts:
            ast_contexts = self._discover_from_ast()
            contexts.extend(ast_contexts)
            if ast_contexts:
                self._canonical_context = ast_contexts[0]
                self._other_contexts = ast_contexts[1:]
        
        return self._canonical_context, self._other_contexts
    
    def _discover_canonical(self) -> Optional[DiscoveryContext]:
        """Discover canonical registry."""
        try:
            module = __import__(self.canonical_module, fromlist=[self.canonical_base])
            base = getattr(module, self.canonical_base)
            if hasattr(base, 'registry'):
                return DiscoveryContext.from_registry(
                    base.registry,
                    is_canonical=True,
                    discovery_method="canonical"
                )
        except Exception as e:
            print(f"  ⚠️ Could not load canonical registry: {e}")
        return None
    
    def _discover_from_gc(self, canonical_context: Optional[DiscoveryContext]) -> List[DiscoveryContext]:
        """
        Single GC iteration to discover all other registries.
        """
        contexts = []
        seen_fingerprints = set()
        
        if canonical_context:
            seen_fingerprints.add(canonical_context.fingerprint_str)
        
        try:
            for obj in gc.get_objects():
                # Check for SQLAlchemy registry
                if not hasattr(obj, 'metadata') or not hasattr(obj, 'mappers'):
                    continue
                
                # Check class name
                class_name = obj.__class__.__name__
                if class_name not in ['registry', 'Registry', 'LocalRegistry']:
                    continue
                
                # Check if this is the canonical registry
                is_canonical = False
                if canonical_context:
                    # Compare fingerprint
                    fp = RegistryFingerprint.from_registry(obj)
                    if str(fp) == canonical_context.fingerprint_str:
                        continue  # Already have canonical
                
                # Generate fingerprint
                fp = RegistryFingerprint.from_registry(obj)
                fp_str = str(fp)
                
                if fp_str in seen_fingerprints:
                    continue
                
                seen_fingerprints.add(fp_str)
                
                context = DiscoveryContext.from_registry(
                    obj,
                    is_canonical=False,
                    discovery_method="gc_discovered"
                )
                contexts.append(context)
                
        except Exception as e:
            print(f"  ⚠️ GC discovery error: {e}")
        
        return contexts
    
    def _discover_from_ast(self) -> List[DiscoveryContext]:
        """AST fallback for registry discovery."""
        import ast
        from pathlib import Path
        
        contexts = []
        backend_dir = Path("backend")
        if not backend_dir.exists():
            return contexts
        
        # Look for declarative_base() and DeclarativeBase
        for py_file in backend_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            try:
                with open(py_file, "r") as f:
                    tree = ast.parse(f.read())
                
                rel_path = py_file.relative_to(Path.cwd())
                module_path = str(rel_path.with_suffix("")).replace("/", ".")
                
                for node in ast.walk(tree):
                    # Pattern 1: Base = declarative_base()
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "Base":
                                if isinstance(node.value, ast.Call):
                                    if (isinstance(node.value.func, ast.Name) and 
                                        node.value.func.id == "declarative_base"):
                                        # Found a Base declaration via AST
                                        # We can't create runtime context here
                                        pass
                    
                    # Pattern 2: class Base(DeclarativeBase):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and base.id == "DeclarativeBase":
                                # Found DeclarativeBase subclass
                                pass
            except Exception:
                continue
        
        return contexts
    
    def get_canonical_context(self) -> Optional[DiscoveryContext]:
        """Get the canonical registry context."""
        return self._canonical_context
    
    def get_all_contexts(self) -> List[DiscoveryContext]:
        """Get all registry contexts."""
        contexts = []
        if self._canonical_context:
            contexts.append(self._canonical_context)
        contexts.extend(self._other_contexts)
        return contexts
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get summary of discovered registries."""
        contexts = self.get_all_contexts()
        return {
            "total_registries": len(contexts),
            "active_registries": sum(1 for c in contexts if c.mapper_count > 0),
            "canonical": self._canonical_context.to_summary() if self._canonical_context else None,
            "others": [c.to_summary() for c in self._other_contexts]
        }
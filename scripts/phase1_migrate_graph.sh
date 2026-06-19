#!/bin/bash
# ============================================================================
# PHASE 1: Graph Consolidation Migration Script
# ============================================================================

cd ~/nemesis_madina

echo "============================================================"
echo "PHASE 1: GRAPH CONSOLIDATION"
echo "============================================================"

# Step 1: Create new graph structure
echo ""
echo "[1/6] Creating new graph structure..."
mkdir -p backend/graph/detectors

# Step 2: Move graph_builder from core
echo ""
echo "[2/6] Moving graph_builder from core..."
if [ -f backend/core/graph_builder.py ]; then
    mv backend/core/graph_builder.py backend/graph/builder.py
    echo "  ✅ Moved backend/core/graph_builder.py -> backend/graph/builder.py"
else
    echo "  ⚠️ backend/core/graph_builder.py not found"
fi

# Step 3: Merge intelligence/graph into backend/graph
echo ""
echo "[3/6] Merging intelligence/graph..."
if [ -d backend/intelligence/graph ]; then
    # Copy collusion detector
    if [ -f backend/intelligence/graph/collusion_detector.py ]; then
        cp backend/intelligence/graph/collusion_detector.py backend/graph/detectors/
        echo "  ✅ Copied collusion_detector.py"
    fi
    # Mark old as deprecated
    echo "# DEPRECATED - Use backend.graph instead" > backend/intelligence/graph/__init__.py
    echo "  ⚠️ Marked intelligence/graph as deprecated"
else
    echo "  ⚠️ backend/intelligence/graph not found"
fi

# Step 4: Update __init__.py
echo ""
echo "[4/6] Updating graph __init__.py..."
cat > backend/graph/__init__.py << 'EOF'
"""
NEMESIS Graph Module - Relationship Graph Management
"""

from backend.graph.models import Graph, GraphNode, GraphEdge, NodeType, EdgeType
from backend.graph.builder import GraphBuilder, build_graph_from_event
from backend.graph.metrics import GraphMetrics
from backend.graph.registry import extractor_registry, register_extractor
from backend.graph.detectors.collusion import CollusionDetector

__all__ = [
    'Graph',
    'GraphNode',
    'GraphEdge',
    'NodeType',
    'EdgeType',
    'GraphBuilder',
    'build_graph_from_event',
    'GraphMetrics',
    'extractor_registry',
    'register_extractor',
    'CollusionDetector'
]
EOF
echo "  ✅ Updated backend/graph/__init__.py"

# Step 5: Update imports across codebase
echo ""
echo "[5/6] Updating imports..."

# Update imports from backend.core.graph_builder
find backend -name "*.py" -type f -exec sed -i 's/from backend\.core\.graph_builder import/from backend.graph.builder import/g' {} \;

# Update imports from backend.intelligence.graph
find backend -name "*.py" -type f -exec sed -i 's/from backend\.intelligence\.graph\.collusion_detector import/from backend.graph.detectors.collusion import/g' {} \;

echo "  ✅ Updated imports"

# Step 6: Verify
echo ""
echo "[6/6] Verifying graph module..."

python -c "
import sys
sys.path.insert(0, '.')

try:
    from backend.graph import Graph, GraphNode, GraphEdge, NodeType, EdgeType
    from backend.graph import GraphBuilder, GraphMetrics, CollusionDetector
    print('  ✅ All graph imports successful')
    
    # Test basic functionality
    from backend.graph import GraphBuilder
    builder = GraphBuilder()
    print('  ✅ GraphBuilder created')
    
    from backend.graph import GraphMetrics
    metrics = GraphMetrics(builder.get_graph())
    print('  ✅ GraphMetrics created')
    
    from backend.graph import CollusionDetector
    detector = CollusionDetector(builder.get_graph())
    print('  ✅ CollusionDetector created')
    
    print('')
    print('  ✅ Graph consolidation complete!')
    
except Exception as e:
    print(f'  ❌ Error: {e}')
    sys.exit(1)
"

echo ""
echo "============================================================"
echo "PHASE 1 COMPLETE"
echo "============================================================"
echo ""
echo "Created files:"
echo "  - backend/graph/models.py"
echo "  - backend/graph/builder.py (moved from core)"
echo "  - backend/graph/registry.py"
echo "  - backend/graph/metrics.py"
echo "  - backend/graph/detectors/collusion.py"
echo ""
echo "Deprecated:"
echo "  - backend/intelligence/graph/ (marked deprecated)"
echo "  - backend/core/graph_builder.py (moved)"
echo ""
echo "Next: Phase 2 - Event Pipeline Hardening"
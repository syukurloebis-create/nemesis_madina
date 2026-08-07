# scripts/metadata_inventory/main.py
import argparse
from .discovery import discover_base_candidates_ast
from .static import StaticAuditor
from .runtime import RuntimeAuditor

def main():
    # Load context
    context = PipelineContext.create(**args)
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["static", "runtime", "full"], default="static")
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()
    
    # Mode Static: 100% aman, tanpa import
    if args.mode in ["static", "full"]:
        static_auditor = StaticAuditor()
        static_results = static_auditor.run()
        static_auditor.report(static_results, args.output_dir)
    
    # Mode Runtime: dengan import, isolated process
    if args.mode in ["runtime", "full"]:
        runtime_auditor = RuntimeAuditor()
        runtime_results = runtime_auditor.run()
        runtime_auditor.report(runtime_results, args.output_dir)

    # Validate pipeline
    pipeline_validator = PipelineValidator()
    pipeline_errors = pipeline_validator.validate(context)
    if pipeline_errors:
        for err in pipeline_errors:
            print(f"❌ Pipeline error: {err.message}")
        sys.exit(2)
    
    # Validate registry
    registry_validator = RegistryValidator()
    registry = FindingRegistry()._load_registry()
    registry_errors = registry_validator.validate(registry)
    if registry_errors:
        for err in registry_errors:
            print(f"❌ Registry error: {err.message}")
        sys.exit(2)
    
    # Run pipeline
    pipeline = AuditPipeline(context)
    result = pipeline.run()
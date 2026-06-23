from core.orchestration.orchestrator import NemesisOrchestrator

def build_orchestrator(
    repository,
    jetstream,
    sequence
):
    return NemesisOrchestrator(
        repository=repository,
        jetstream=jetstream,
        sequence=sequence
    )
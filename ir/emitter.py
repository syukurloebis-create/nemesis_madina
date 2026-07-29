# ir/emitter.py

from typing import Optional
from .context import IRContext
from .models import Module


class Emitter:
    def __init__(self, context: IRContext):
        self.context = context

    def emit_module(self, name: str, file: str, file_hash: str) -> int:
        module_id = self.context.module_alloc.allocate()
        module = Module(
            module_id=module_id,
            name=name,
            file=file,
            file_hash=file_hash
        )
        self.context.modules.insert(module)
        return module_id

    def emit_class(
        self,
        name: str,
        qualname: str,
        module_id: int,
        scope_id: int,
        location_id: int,
        bases: list,
        decorators: list,
    ) -> int:
        raise NotImplementedError("emit_class not implemented in CP1")

    def emit_function(
        self,
        name: str,
        qualname: str,
        module_id: int,
        scope_id: int,
        location_id: int,
        params: list,
        returns: Optional[str],
    ) -> int:
        raise NotImplementedError("emit_function not implemented in CP1")

    def emit_assign(
        self,
        module_id: int,
        scope_id: int,
        ordinal: int,
        location_id: int,
        targets: list,
        value: dict,
    ) -> int:
        raise NotImplementedError("emit_assign not implemented in CP1")
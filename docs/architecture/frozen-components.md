# \# Frozen Components

# 

# Komponen-komponen berikut dibekukan (frozen) dan tidak aktif di production execution path.

# 

# Keputusan ini didokumentasikan di \[ADR-030](adr/ADR-030-architecture-freeze.md).

# 

# \## Prinsip

# 

# > Frozen components are not deprecated. They are intentionally preserved architectural assets.

# > Freeze is a governance state rather than a lifecycle end-state.

# 

# \## Type A — Dormant Runtime

# 

# | ID | Komponen | File | Status |

# | :--- | :--- | :--- | :--- |

# | FR-001 | GetDashboardQueryHandler | `backend/application/queries/get\_dashboard\_handler.py` | Frozen |

# | FR-002 | GetDashboardQuery | `backend/application/queries/dashboard\_query.py` | Frozen |

# | FR-003 | DashboardReadRepository | `backend/infrastructure/repositories/dashboard\_read\_repository.py` | Frozen |

# | FR-004 | DashboardProjection | `backend/infrastructure/projections/dashboard\_projection.py` | Frozen |

# | FR-005 | WorkflowService | `backend/services/workflow\_service.py` | Frozen |

# 

# \## Type B — Architectural Preservation

# 

# | ID | Komponen | File | ADR Reference |

# | :--- | :--- | :--- | :--- |

# | FR-006 | ProjectionRebuilder | `backend/infrastructure/projections/rebuild.py` | ADR-027 |

# | FR-007 | ProjectionCheckpoint | `backend/infrastructure/models/projection\_checkpoint.py` | ADR-027 |

# | FR-008 | OutboxPublisher | `backend/infrastructure/outbox/publisher.py` | ADR-020 |

# | FR-009 | AnalyzeCaseCommandHandler | `backend/application/commands/analysis\_mapper.py` | ADR-020 |

# 

# \## Freeze Register

# 

# Lihat \[freeze-register.md](freeze-register.md) untuk status terkini dan histori review.


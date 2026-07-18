# \# Architecture Inventory - Pilot Migration

# 

# \## 1. Service → Model → Table Mapping

# 

# | Service | Model | Table | Future Repository |

# |---------|-------|-------|-------------------|

# | DashboardIntelligenceService | - | - | CaseRepository |

# | CaseService | Case | cases | CaseRepository |

# | EvidenceService | Evidence | evidence | EvidenceRepository |

# | WorkflowService | Workflow | workflows | WorkflowRepository |

# | SnapshotService | Snapshot | snapshots | SnapshotRepository |

# 

# \## 2. Current Event Flow (Dashboard Intelligence)


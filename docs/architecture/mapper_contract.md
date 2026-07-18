# \# docs/architecture/mapper\_contract.md - FINAL

# 

# \## Mapper Categories

# 

# \### Projection Mapper (DTO + Calculated → Summary)

# 

# Mapper ini menggabungkan dua sumber data:

# 

# | Mapper | Input | Output |

# |--------|-------|--------|

# | RiskMapper | RiskCollectorDTO + CalculatedRisk | RiskSummary |

# | FraudMapper | FraudCollectorDTO + CalculatedFraud | FraudSummary |

# | EvidenceMapper | EvidenceCollectorDTO + CalculatedEvidence | EvidenceSummary |

# 

# \### Direct Mapper (DTO → Summary)

# 

# Mapper ini melakukan transformasi langsung:

# 

# | Mapper | Input | Output |

# |--------|-------|--------|

# | GraphMapper | GraphCollectorDTO | GraphSummary |

# | ProcurementMapper | ProcurementCollectorDTO | ProcurementSummary |

# 

# \## Contract Rules (ALL Mappers)

# 

# Mapper SHALL:

# \- Transform input(s) → Summary

# \- Preserve metadata (engine\_status, error)

# \- Use `engine\_status` to determine data availability

# 

# Mapper SHALL NOT:

# \- Query database

# \- Calculate scores

# \- Determine risk levels

# \- Aggregate repository

# \- Execute business rules

# \- Interpret business meaning


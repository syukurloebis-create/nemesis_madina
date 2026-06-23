export const transformDashboardData = (raw: any) => {
  return {
    executive: {
      totalCases: raw.cases?.total_cases || 0,
      activeCases: raw.cases?.active_cases || 0,
      highRiskCases: raw.cases?.high_risk_cases || 0,
      criticalAlerts: raw.fraud?.critical_alerts || 0,
      avgResolutionTime: raw.cases?.avg_resolution_time || 0,
      riskScore: raw.risk?.score || 0,
    },
    cases: raw.cases?.recent || [],
    evidence: raw.evidence || {},
    graph: raw.graph || {},
    fraud: raw.fraud || {},
    rup: raw.procurement || {},
    stats: raw.cases || {},
    risk: raw.risk || {},
    recommendations: raw.recommendations || [],
    systemStatus: {
      isOnline: true,
      lastUpdate: new Date(),
      services: {
        api: true,
        database: true,
        graphEngine: true,
        aiEngine: true,
      },
      metrics: {
        responseTime: 150,
        uptime: 99.9,
        memoryUsage: 45,
      },
    },
  };
};

export default transformDashboardData;

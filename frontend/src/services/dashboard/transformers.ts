/**
 * NEMESIS V8+ - Dashboard Data Transformers
 * WITH ADAPTIVE UNWRAP - Handle semua response format
 */

// ============================================
// UNWRAP - Extract data dari berbagai wrapper
// ============================================

function unwrap(data: any): any {
  if (!data) return {};
  
  // Jika array, return array
  if (Array.isArray(data)) return data;
  
  // Jika ada data property
  if (data.data !== undefined) {
    const unwrapped = unwrap(data.data);
    if (unwrapped && typeof unwrapped === 'object' && Object.keys(unwrapped).length > 0) {
      return unwrapped;
    }
    return data.data;
  }
  
  // Jika ada result property
  if (data.result !== undefined) {
    const unwrapped = unwrap(data.result);
    if (unwrapped && typeof unwrapped === 'object' && Object.keys(unwrapped).length > 0) {
      return unwrapped;
    }
    return data.result;
  }
  
  // Jika ada stats property
  if (data.stats !== undefined) {
    const unwrapped = unwrap(data.stats);
    if (unwrapped && typeof unwrapped === 'object' && Object.keys(unwrapped).length > 0) {
      return unwrapped;
    }
    return data.stats;
  }
  
  // Jika ada items property (untuk list)
  if (data.items !== undefined && Array.isArray(data.items)) {
    return data.items;
  }
  
  // Jika sudah memiliki total/open, return langsung
  if (data.total !== undefined || data.open !== undefined || data.avg_risk_score !== undefined) {
    return data;
  }
  
  // Coba cari field yang mengandung data
  for (const key of Object.keys(data)) {
    const value = data[key];
    if (value && typeof value === 'object') {
      if (value.total !== undefined || value.open !== undefined || value.avg_risk_score !== undefined) {
        return unwrap(value);
      }
      if (Array.isArray(value) && value.length > 0) {
        return value;
      }
    }
  }
  
  return data;
}

// ============================================
// TRANSFORMER
// ============================================

export function transformDashboardData(raw: any) {
  console.log('[Transformers] 📥 RAW INPUT:', JSON.stringify(raw, null, 2));
  
  if (!raw || typeof raw !== 'object') {
    console.error('[Transformers] ❌ Invalid raw data');
    return getDefaultDashboard();
  }

  // Unwrap semua data
  const cases = unwrap(raw.cases);
  const fraud = unwrap(raw.fraud);
  const graph = unwrap(raw.graph);
  const risk = unwrap(raw.risk);
  const alerts = unwrap(raw.alerts);
  const investigations = Array.isArray(raw.investigations) ? raw.investigations : [];

  console.log('[Transformers] 📊 CASES (unwrapped):', JSON.stringify(cases, null, 2));
  console.log('[Transformers] 📊 FRAUD (unwrapped):', JSON.stringify(fraud, null, 2));
  console.log('[Transformers] 📊 GRAPH (unwrapped):', JSON.stringify(graph, null, 2));
  console.log('[Transformers] 📊 INVESTIGATIONS:', investigations.length);

  // ============================================
  // EKSTRAKSI DENGAN MULTIPLE FALLBACK
  // ============================================

  // Cases
  const totalCases = Number(
    cases?.total ?? 
    cases?.total_cases ?? 
    cases?.count ?? 
    0
  );
  
  const activeCases = Number(
    cases?.open ?? 
    cases?.active ?? 
    cases?.active_cases ?? 
    cases?.activeCount ?? 
    0
  );
  
  const investigatingCases = Number(
    cases?.investigating ?? 
    cases?.in_progress ?? 
    cases?.investigatingCount ?? 
    0
  );
  
  const closedCases = Number(
    cases?.closed ?? 
    cases?.completed ?? 
    cases?.closedCount ?? 
    0
  );
  
  const riskScore = Number(
    cases?.avg_risk_score ?? 
    cases?.risk_score ?? 
    cases?.average_risk ?? 
    cases?.riskScore ?? 
    risk?.score ?? 
    0
  );
  
  const avgResolutionTime = Number(
    cases?.avg_resolution_time ?? 
    cases?.averageResolutionTime ?? 
    0
  );

  // Fraud
  const fraudTotal = Number(
    fraud?.total ?? 
    fraud?.total_fraud ?? 
    fraud?.count ?? 
    0
  );
  
  const activeAlerts = Number(
    fraud?.active_alerts ?? 
    fraud?.alerts ?? 
    fraud?.alert_count ?? 
    fraud?.activeAlerts ?? 
    0
  );
  
  const highConfidence = Number(
    fraud?.high_confidence ?? 
    fraud?.highConfidence ?? 
    0
  );
  
  const collusion = Number(
    fraud?.collusion ?? 
    fraud?.collusion_count ?? 
    0
  );

  // Graph
  const entities = Number(
    graph?.total_entities ?? 
    graph?.entities ?? 
    graph?.entity_count ?? 
    graph?.nodes ?? 
    0
  );
  
  const relationships = Number(
    graph?.total_relationships ?? 
    graph?.relationships ?? 
    graph?.relationship_count ?? 
    graph?.edges ?? 
    0
  );
  
  const collusionEdges = Number(
    graph?.collusion_edges ?? 
    graph?.collusionEdges ?? 
    0
  );

  // Risk
  const riskLevel = risk?.level ?? determineRiskLevel(riskScore);

  // Alerts
  const alertTotal = Number(
    alerts?.total ?? 
    activeAlerts ?? 
    0
  );
  
  const newAlerts = Number(
    alerts?.new ?? 
    alerts?.new_alerts ?? 
    0
  );
  
  const criticalAlerts = Number(
    alerts?.critical ?? 
    alerts?.critical_alerts ?? 
    activeAlerts ?? 
    0
  );

  console.log('[Transformers] 📊 EXTRACTED VALUES:', {
    totalCases,
    activeCases,
    investigatingCases,
    closedCases,
    riskScore,
    fraudTotal,
    activeAlerts,
    entities,
    relationships,
    investigations: investigations.length,
  });

  // ============================================
  // BUILD RESULT
  // ============================================

  const result = {
    executive: {
      totalCases,
      activeCases,
      investigatingCases,
      closedCases,
      highRiskCases: cases?.high_risk ?? 0,
      criticalAlerts: criticalAlerts,
      avgResolutionTime,
      riskScore,
      recoveryValue: cases?.recovered_value ?? 0,
      exposureValue: cases?.exposure_value ?? 0,
    },
    stats: cases,
    cases: Array.isArray(cases?.recent) ? cases.recent : [],
    evidence: raw.evidence || {},
    graph: {
      entities,
      relationships,
      collusionEdges,
      metrics: graph,
      keyActors: graph?.key_actors || [],
      communities: graph?.communities || [],
    },
    fraud: {
      total: fraudTotal,
      collusion,
      activeAlerts,
      highConfidence,
      patterns: fraud?.patterns || [],
      signals: fraud?.signals || [],
    },
    risk: {
      score: riskScore,
      level: riskLevel,
      factors: risk?.factors || [],
      explanations: risk?.explanations || [],
    },
    alerts: {
      total: alertTotal,
      new: newAlerts,
      critical: criticalAlerts,
      list: alerts?.list || [],
    },
    vendors: Array.isArray(raw.vendors) ? raw.vendors : [],
    recommendations: Array.isArray(raw.recommendations) ? raw.recommendations : [],
    investigations: investigations,
    systemStatus: {
      isOnline: true,
      lastUpdate: new Date(),
      services: { api: true, database: true, graphEngine: true, aiEngine: true },
      metrics: { responseTime: 150, uptime: 99.9, memoryUsage: 45 },
    },
  };

  console.log('[Transformers] ✅ FINAL OUTPUT:', {
    totalCases: result.executive.totalCases,
    riskScore: result.executive.riskScore,
    activeCases: result.executive.activeCases,
    criticalAlerts: result.executive.criticalAlerts,
    fraudTotal: result.fraud.total,
    entities: result.graph.entities,
    relationships: result.graph.relationships,
    investigations: result.investigations.length,
  });

  if (result.executive.totalCases === 0 && result.executive.riskScore === 0) {
    console.warn('[Transformers] ⚠️ WARNING: All values are 0!');
    console.warn('[Transformers] 📊 Raw cases structure:', JSON.stringify(raw.cases, null, 2));
    console.warn('[Transformers] 📊 Unwrapped cases:', cases);
  }

  return result;
}

function determineRiskLevel(score: number): string {
  if (score >= 80) return 'KRITIS';
  if (score >= 60) return 'TINGGI';
  if (score >= 40) return 'SEDANG';
  return 'RENDAH';
}

function getDefaultDashboard() {
  return {
    executive: {
      totalCases: 0,
      activeCases: 0,
      investigatingCases: 0,
      closedCases: 0,
      highRiskCases: 0,
      criticalAlerts: 0,
      avgResolutionTime: 0,
      riskScore: 0,
      recoveryValue: 0,
      exposureValue: 0,
    },
    stats: {},
    cases: [],
    evidence: {},
    graph: { entities: 0, relationships: 0 },
    fraud: { total: 0, activeAlerts: 0 },
    risk: { score: 0, level: 'RENDAH' },
    alerts: { total: 0 },
    vendors: [],
    recommendations: [],
    investigations: [],
    systemStatus: { isOnline: true },
  };
}

export default transformDashboardData;

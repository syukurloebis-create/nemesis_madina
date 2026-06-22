// Dashboard APIs
export const getDashboardData = () =>
    api.get('/api/v1/dashboard/overview');


export const getStrategicDashboard = () =>
    api.get('/api/v1/dashboard/strategic');


// Compatibility aliases
export const getExecutiveOverview = () =>
    api.get('/api/v1/dashboard/overview');


export const getExecutiveRiskMap = () =>
    api.get('/api/v1/dashboard/strategic');


export const getExecutiveTrend = () =>
    api.get('/api/v1/dashboard/strategic');


export const getGovernanceMetrics = () =>
    api.get('/api/v1/dashboard/strategic');
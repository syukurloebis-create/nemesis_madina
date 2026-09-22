import {
 BrowserRouter,
 Routes,
 Route,
 Navigate
} from 'react-router-dom';

import Dashboard from './pages/Dashboard';
import Risk from './pages/Risk';

import LiveAlerts from './pages/LiveAlerts';
import VendorList from './pages/VendorList';
import ProcurementDashboard from './pages/ProcurementDashboard';
import Analytics from './pages/Analytics';
import InvestigationCase from './pages/InvestigationCase';

import RiskExposure from './pages/RiskExposure';
import RecoveryIntelligence from './pages/RecoveryIntelligence';

import IntelligenceDashboard from './pages/IntelligenceDashboard';
import GraphIntelligence from './pages/GraphIntelligence';
import CollusionGraphPage from './pages/CollusionGraphPage';
import IntelligenceReports from './pages/IntelligenceReports';

import InvestigationWorkspace from './components/investigation/InvestigationWorkspace';

// Import Login
import Login from './pages/Login';

function App(){
  return (
    <BrowserRouter>
      <Routes>
        {/* Route Login */}
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route path="/" element={<Dashboard/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
        <Route path="/investigation" element={<InvestigationWorkspace/>}/>
        <Route path="/alerts" element={<LiveAlerts/>}/>
        <Route path="/vendors" element={<VendorList/>}/>
        <Route path="/procurement" element={<ProcurementDashboard/>}/>
        <Route path="/analytics" element={<Analytics/>}/>
        <Route path="/cases" element={<InvestigationCase/>}/>
        <Route path="/risk" element={<Risk/>}/>
        <Route path="/risk/exposure" element={<RiskExposure/>}/>
        <Route path="/recovery" element={<RecoveryIntelligence/>}/>
        <Route path="/intelligence" element={<IntelligenceDashboard/>}/>
        <Route path="/reports" element={<IntelligenceReports/>}/>
        <Route path="/recovery/:caseId" element={<RecoveryIntelligence/>}/>

        {/* Graph Intelligence — Phase B */}
        <Route path="/graph-intelligence" element={<GraphIntelligence/>} />
        <Route path="/collusion-graph" element={<CollusionGraphPage/>} />

        {/* Fallback - jika route tidak ditemukan, redirect ke login atau dashboard */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

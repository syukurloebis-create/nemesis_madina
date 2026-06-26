import {
 BrowserRouter,
 Routes,
 Route
} from 'react-router-dom';


import Dashboard from './pages/Dashboard';
import Risk from './pages/Risk';
import ComingSoon from './pages/ComingSoon';

import LiveAlerts from './pages/LiveAlerts';
import VendorList from './pages/VendorList';
import ProcurementDashboard from './pages/ProcurementDashboard';
import Analytics from './pages/Analytics';
import InvestigationCase from './pages/InvestigationCase';

import RiskExposure from './pages/RiskExposure';
import RecoveryIntelligence from './pages/RecoveryIntelligence';

import IntelligenceDashboard from './pages/IntelligenceDashboard';
import IntelligenceReports from './pages/IntelligenceReports';

import InvestigationWorkspace from './components/investigation/InvestigationWorkspace';


function App(){

return (

<BrowserRouter>

<Routes>


<Route path="/" element={<Dashboard/>}/>
<Route path="/dashboard" element={<Dashboard/>}/>


<Route 
path="/investigation"
element={<InvestigationWorkspace/>}
/>


<Route 
path="/alerts"
element={<LiveAlerts/>}
/>


<Route 
path="/vendors"
element={<VendorList/>}
/>


<Route 
path="/procurement"
element={<ProcurementDashboard/>}
/>


<Route 
path="/analytics"
element={<Analytics/>}
/>


<Route
path="/cases"
element={<InvestigationCase/>}
/>


<Route
path="/risk"
element={<Risk/>}
/>


<Route
path="/risk/exposure"
element={<RiskExposure/>}
/>


<Route
path="/recovery"
element={<RecoveryIntelligence/>}
/>


<Route
path="/intelligence"
element={<IntelligenceDashboard/>}
/>


<Route
path="/reports"
element={<IntelligenceReports/>}
/>


<Route
path="*"
element={<Dashboard/>}
/>


</Routes>

</BrowserRouter>

)

}


export default App;
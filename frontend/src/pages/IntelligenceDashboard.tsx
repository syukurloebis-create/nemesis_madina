import React from 'react';

import AIStatusBar 
from '../components/intelligence/AIStatusBar';

import RiskReasoningPanel
from '../components/intelligence/RiskReasoningPanel';

import RecommendationCenter
from '../components/intelligence/RecommendationCenter';


import DecisionCenter
from '../components/decision/DecisionCenter';



export default function IntelligenceDashboard(){

const caseId =
'446e216d-eb0e-487e-8e6b-ec943468ea20';


return (

<div className="min-h-screen bg-gray-900 p-6">


<div className="mb-6">

<h1 className="text-3xl font-bold text-white">
🧠 NEMESIS AI Intelligence Center
</h1>


<p className="text-gray-400">
Autonomous risk reasoning and decision intelligence
</p>

</div>



<AIStatusBar
 caseId={caseId}
/>



<div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">


<div>

<RiskReasoningPanel
caseId={caseId}
/>

</div>



<div>

<RecommendationCenter
caseId={caseId}
/>

</div>


</div>




<div className="mt-6">

<DecisionCenter
caseId={caseId}
/>

</div>



</div>

);

}
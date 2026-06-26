import React from 'react';
import RiskReasoningPanel from '../components/intelligence/RiskReasoningPanel';

export default function Risk(){

const caseId =
'446e216d-eb0e-487e-8e6b-ec943468ea20';


return (

<div className="min-h-screen bg-gray-900 p-6">

<h1 className="text-3xl font-bold text-white">
Risk Intelligence Center
</h1>


<p className="text-gray-400 mb-6">
AI powered risk reasoning
</p>


<RiskReasoningPanel caseId={caseId}/>


</div>

);

}

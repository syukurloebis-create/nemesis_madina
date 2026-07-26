import React from "react";
import {
  ShieldAlert,
  Network,
  FileCheck,
  Activity
} from "lucide-react";


interface AIStatusBarProps {

  intelligence?: any;

  caseId?: string;

}



const AIStatusBar:React.FC<AIStatusBarProps> = ({
  intelligence,
  caseId
})=>{


const fraud =
  intelligence?.fraud ?? {};


const risk =
  intelligence?.risk ?? {};


const graph =
  intelligence?.graph ?? {};


const evidence =
  intelligence?.evidence ?? {};



const fraudRisk =
  fraud.overall_risk ?? "NORMAL";


const riskScore =
  risk.score ?? 0;


const riskLevel =
  risk.level ?? "UNKNOWN";


const alerts =
  fraud.active_alerts ?? 0;


const entities =
  graph.entities ?? 0;


const relations =
  graph.relationships ?? 0;


const evidenceScore =
  evidence.score ?? 0;



const statusColor =
fraudRisk==="CRITICAL"
?
"bg-red-500/20 text-red-400 border-red-500/40"

:

fraudRisk==="HIGH"
?
"bg-orange-500/20 text-orange-400 border-orange-500/40"

:
"bg-green-500/20 text-green-400 border-green-500/40";



return (

<div
className="
bg-gray-900
border
border-gray-700
rounded-xl
p-4
space-y-4
"
>


<div
className="
flex
justify-between
items-center
"
>


<div>

<h2
className="
text-white
font-bold
text-lg
"
>
Executive AI Intelligence Status
</h2>


<p
className="
text-xs
text-gray-400
"
>
Case:
{caseId}
</p>

</div>



<div
className={`
px-4
py-2
rounded-lg
border
font-bold
${statusColor}
`}
>

{fraudRisk}

</div>


</div>





<div
className="
grid
grid-cols-2
md:grid-cols-4
gap-3
"
>



<div
className="
bg-gray-800
rounded-lg
p-3
"
>

<ShieldAlert
className="
text-red-400
mb-2
"
/>

<p className="text-xs text-gray-400">
Fraud Alerts
</p>

<p className="text-2xl text-white font-bold">
{alerts}
</p>

</div>





<div
className="
bg-gray-800
rounded-lg
p-3
"
>

<Activity
className="text-yellow-400 mb-2"
/>

<p className="text-xs text-gray-400">
Risk Score
</p>

<p className="text-2xl text-white font-bold">
{riskScore}
</p>

<p className="text-xs text-gray-400">
{riskLevel}
</p>

</div>





<div
className="
bg-gray-800
rounded-lg
p-3
"
>

<Network
className="text-blue-400 mb-2"
/>

<p className="text-xs text-gray-400">
Entity Graph
</p>

<p className="text-2xl text-white font-bold">
{entities}
</p>

<p className="text-xs text-gray-400">
{relations} relations
</p>


</div>





<div
className="
bg-gray-800
rounded-lg
p-3
"
>

<FileCheck
className="text-green-400 mb-2"
/>

<p className="text-xs text-gray-400">
Evidence Score
</p>

<p className="text-2xl text-white font-bold">
{evidenceScore}
</p>


</div>



</div>



</div>

)


};


export default AIStatusBar;
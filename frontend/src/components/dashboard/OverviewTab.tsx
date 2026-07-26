// OverviewTab.tsx
// Executive Intelligence Summary V7

import React from "react";

import {
  ShieldAlert,
  AlertTriangle,
  FileCheck,
  Activity,
  Network,
  ArrowRight
} from "lucide-react";


import {
  IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props {


 intelligence: IntelligenceModel;


 onAction?:
 (action:string)=>void;


}






const riskStyle = (
level:string
)=>{


switch(level){


case "CRITICAL":

return {
color:"text-red-400",
bg:"bg-red-500/10",
border:"border-red-500/40"
};



case "HIGH":

return {
color:"text-orange-400",
bg:"bg-orange-500/10",
border:"border-orange-500/40"
};



case "MEDIUM":

return {
color:"text-yellow-400",
bg:"bg-yellow-500/10",
border:"border-yellow-500/40"
};



default:

return {
color:"text-green-400",
bg:"bg-green-500/10",
border:"border-green-500/40"
};


}


};








export default function OverviewTab({

 intelligence,

 onAction

}:Props){



const risk =
riskStyle(
 intelligence.risk.level
);




return (

<div

className="
space-y-6
"

>



{/* EXECUTIVE SUMMARY */}


<div

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
"

>


<div

className="
flex
justify-between
items-start
"

>


<div>


<h2

className="
text-xl
font-bold
text-white
flex
items-center
gap-2
"

>


<Activity

className="
text-primary-400
"

/>


Executive Intelligence Summary


</h2>



<p

className="
text-sm
text-gray-400
mt-1
"

>

Real-time investigation posture from intelligence engine

</p>


</div>




<div

className={`
px-4
py-2
rounded-lg
border
${risk.bg}
${risk.border}
`}

>


<p

className="
text-xs
text-gray-400
"

>

Risk Level

</p>


<p

className={`
text-xl
font-bold
${risk.color}
`}

>

{intelligence.risk.level}

</p>


</div>



</div>





<div

className="
grid
grid-cols-1
md:grid-cols-4
gap-4
mt-6
"

>



{/* Risk Score */}


<div

className="
rounded-lg
bg-gray-900
border
border-gray-700
p-4
"

>

<p className="
text-xs
text-gray-400
">

Risk Score

</p>


<p className="
text-3xl
font-bold
text-white
">

{
intelligence.risk.score
}

</p>


</div>





{/* Alerts */}


<div

className="
rounded-lg
bg-gray-900
border
border-gray-700
p-4
"

>


<p className="
text-xs
text-gray-400
flex
gap-2
items-center
">

<AlertTriangle
className="
w-4
h-4
text-red-400
"
/>

Active Alerts

</p>


<p

className="
text-3xl
font-bold
text-red-400
"

>

{
intelligence.fraud.active_alerts
}

</p>


</div>





{/* Findings */}


<div

className="
rounded-lg
bg-gray-900
border
border-gray-700
p-4
"

>


<p

className="
text-xs
text-gray-400
flex
gap-2
"

>

<ShieldAlert

className="
w-4
h-4
text-orange-400
"

/>


Findings


</p>


<p

className="
text-3xl
font-bold
text-orange-400
"

>

{
intelligence.findings.total
}


</p>


</div>





{/* Evidence */}


<div

className="
rounded-lg
bg-gray-900
border
border-gray-700
p-4
"

>


<p

className="
text-xs
text-gray-400
flex
gap-2
"

>


<FileCheck

className="
w-4
h-4
text-blue-400
"

/>


Evidence


</p>


<p

className="
text-3xl
font-bold
text-blue-400
"

>

{
intelligence.evidence.score
}

%

</p>


</div>



</div>


</div>








{/* INVESTIGATION POSTURE */}


<div

className="
grid
grid-cols-1
lg:grid-cols-3
gap-5
"

>



<div

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-5
"

>


<h3

className="
text-white
font-semibold
mb-3
"

>

Fraud Intelligence

</h3>



<div className="
space-y-2
text-sm
text-gray-300
">


<p>

Risk:

<span className="text-white ml-2">

{
intelligence.fraud.overall_risk
}

</span>

</p>


<p>

High Confidence Signals:

<span className="text-white ml-2">

{
intelligence.fraud.high_confidence
}

</span>


</p>


</div>



<button

onClick={()=>onAction?.("signals")}

className="
mt-4
flex
items-center
gap-2
text-primary-400
text-sm
"

>

Open Fraud Signals

<ArrowRight
className="
w-4
h-4
"
/>

</button>



</div>








<div

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-5
"

>


<h3

className="
text-white
font-semibold
mb-3
"

>

Graph Intelligence


</h3>


<div

className="
flex
items-center
gap-3
"

>


<Network
className="
text-purple-400
"
/>


<div>


<p className="
text-gray-400
text-xs
">

Entity Network

</p>


<p className="
text-white
font-bold
"

>

{
intelligence.graph.entities
}

entities

/

{
intelligence.graph.relationships
}

relations


</p>


</div>


</div>



<button

onClick={()=>onAction?.("network")}

className="
mt-4
flex
items-center
gap-2
text-primary-400
text-sm
"

>

Open Network Explorer

<ArrowRight
className="
w-4
h-4
"
/>


</button>



</div>







<div

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-5
"

>


<h3

className="
text-white
font-semibold
mb-3
"

>

Investigation Status

</h3>



<p className="
text-gray-400
text-sm
"

>

Case Status

</p>


<p

className="
text-white
font-bold
mt-1
"

>

{
intelligence.risk.case_status
}

</p>




<button

onClick={()=>onAction?.("investigation")}

className="
mt-4
flex
items-center
gap-2
text-primary-400
text-sm
"

>


Open Investigation


<ArrowRight
className="
w-4
h-4
"
/>


</button>



</div>




</div>







</div>

);


}
// IntelligenceTabs.tsx
// Executive Intelligence Command Center Tab Controller V1

import React from "react";

import {
  LayoutDashboard,
  ShieldAlert,
  Network,
  Search,
  FileCheck,
  Clock3,
  RotateCcw,
  Gavel
} from "lucide-react";

import GraphEntityExplorer
from "../graph/GraphEntityExplorer";

import OverviewTab from "../dashboard/OverviewTab";

import RiskReasoningPanel
from "./RiskReasoningPanel";

import GraphIntelligence
from "../graph/GraphIntelligence";


import FraudSignalExplorer
from "./FraudSignalExplorer";


import EvidenceHealthPanel
from "./EvidenceHealthPanel";


import InvestigationTimeline
from "./InvestigationTimeline";


import RecoveryIntelligence
from "../../pages/RecoveryIntelligence";


import DecisionCenter
from "../decision/DecisionCenter";


import InvestigationWorkspace
from "../investigation/InvestigationWorkspace";



import {
  IntelligenceModel
} from "../../services/intelligenceAdapter";




interface Props {


 intelligence:
 IntelligenceModel;



 activeTab:string;


 setActiveTab:
 (tab:string)=>void;



 caseId:string;



 userId?:string;



 onAction?:
 (action:string)=>void;


}





interface TabItem {


id:string;


label:string;


icon:any;


}



const tabs:TabItem[]=[


{
 id:"overview",
 label:"Executive Overview",
 icon:LayoutDashboard
},


{
 id:"risk",
 label:"Risk Reasoning",
 icon:ShieldAlert
},


{
 id:"network",
 label:"Graph Intelligence",
 icon:Network
},


{
 id:"signals",
 label:"Fraud Signals",
 icon:Search
},


{
 id:"evidence",
 label:"Evidence Health",
 icon:FileCheck
},


{
 id:"timeline",
 label:"Investigation Timeline",
 icon:Clock3
},


{
 id:"investigation",
 label:"Investigation",
 icon:Search
},


{
 id:"recovery",
 label:"Recovery",
 icon:RotateCcw
},


{
 id:"decision",
 label:"Decision",
 icon:Gavel
}


];





export default function IntelligenceTabs({

 intelligence,

 activeTab,

 setActiveTab,

 caseId,

 userId="user-123",

 onAction


}:Props){





return (

<div className="
space-y-6
">



{/* TAB NAVIGATION */}


<div
className="
bg-dark-card
border
border-dark-border
rounded-xl
p-2
overflow-x-auto
"
>


<div
className="
flex
gap-2
min-w-max
"
>


{
tabs.map(
(tab)=>

{


const Icon =
tab.icon;


const active =
activeTab===tab.id;



return (

<button

key={tab.id}


onClick={()=>setActiveTab(tab.id)}


className={`
flex
items-center
gap-2
px-4
py-2
rounded-lg
text-sm
transition-all

${
active

?

"bg-primary-600 text-white shadow-lg"

:

"text-gray-400 hover:bg-gray-800 hover:text-white"

}

`}

>


<Icon
className="
w-4
h-4
"
/>


{tab.label}


</button>


)


}

)

}



</div>


</div>





{/* CONTENT AREA */}



<div>



{
activeTab==="overview"

&&

<OverviewTab

intelligence={intelligence}

onAction={
onAction
}

/>

}





{
activeTab==="risk"

&&

<RiskReasoningPanel

intelligence={intelligence}

/>

}




{
activeTab==="network"

&&

<div className="space-y-6">

<GraphIntelligence

intelligence={intelligence}

/>


<GraphEntityExplorer

intelligence={intelligence}

/>


</div>

}




{
activeTab==="signals"

&&

<FraudSignalExplorer

intelligence={intelligence}

/>

}




{
activeTab==="evidence"

&&

<EvidenceHealthPanel

intelligence={intelligence}

/>

}




{
activeTab==="timeline"

&&

<InvestigationTimeline

intelligence={intelligence}

/>

}





{
activeTab==="investigation"

&&

<InvestigationWorkspace

caseId={caseId}

/>

}




{
activeTab==="recovery"

&&

<RecoveryIntelligence/>

}





{
activeTab==="decision"

&&

<DecisionCenter

caseId={caseId}

userId={userId}

/>

}




</div>



</div>


);


}
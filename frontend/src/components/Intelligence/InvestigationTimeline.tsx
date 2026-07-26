import React, {
useMemo,
useState
} from "react";

import {
Clock,
ChevronDown,
ChevronRight,
User,
ShieldAlert,
FileCheck,
Activity,
AlertTriangle
} from "lucide-react";


import {
IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props {

 intelligence: IntelligenceModel;

}



interface TimelineItem {

findingId:string;

title:string;

severity:string;

status:string;

engine:string;

timeline:any;

decision:any;

evidence:any;

recommendations:string[];

}




const severityStyle = (
severity:string
)=>{


switch(
severity
?.toUpperCase()
){

case "CRITICAL":

return {
badge:
"bg-red-500/20 text-red-400 border-red-500/40",
dot:
"bg-red-500"
};


case "HIGH":

return {
badge:
"bg-orange-500/20 text-orange-400 border-orange-500/40",
dot:
"bg-orange-500"
};


case "MEDIUM":

return {
badge:
"bg-yellow-500/20 text-yellow-400 border-yellow-500/40",
dot:
"bg-yellow-500"
};


default:

return {
badge:
"bg-blue-500/20 text-blue-400 border-blue-500/40",
dot:
"bg-blue-500"
};

}

};





export default function InvestigationTimeline({

intelligence

}:Props){



const [
expanded,
setExpanded
]=useState<string|null>(null);





const items =
useMemo(()=>{


return (

intelligence
?.findings
?.findings
??
[]

)

.map(
(
finding:any
):TimelineItem=>(

{

findingId:
finding.id,

title:
finding.title,

severity:
finding.severity,

status:
finding.status,

engine:
finding.engine,

timeline:
finding.intelligence?.timeline
??

{},

decision:
finding.intelligence?.decision
??

{},

evidence:
finding.intelligence?.evidence
??

{},

recommendations:
finding.intelligence?.recommendations
??

[]

}

)

);


},[
intelligence
]);





if(!items.length){

return (

<div className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
text-gray-400
text-center
">

No investigation timeline available

</div>

);

}





return (

<div className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
space-y-5
">



<div className="
flex
items-center
gap-3
">

<Activity
className="
text-primary-400
"
/>


<div>

<h2 className="
text-xl
font-bold
text-white
">

Investigation Timeline

</h2>


<p className="
text-sm
text-gray-400
">

Finding lifecycle, analyst actions and evidence events

</p>


</div>


</div>





<div className="
space-y-4
">


{
items.map(
(item)=>{


const style =
severityStyle(
item.severity
);


const open =
expanded === item.findingId;



return (

<div

key={item.findingId}

className="
border
border-gray-700
rounded-xl
overflow-hidden
"

>


<button

onClick={()=>


setExpanded(
open
?
null
:
item.findingId
)

}

className="
w-full
flex
items-center
gap-4
p-4
hover:bg-gray-800/60
transition
text-left
"

>


{
open

?

<ChevronDown
className="w-5 h-5 text-gray-400"
/>

:

<ChevronRight
className="w-5 h-5 text-gray-400"
/>

}



<div
className={`
w-3
h-3
rounded-full
${style.dot}
`}
/>



<div className="flex-1">


<div className="
flex
gap-3
items-center
">

<h3 className="
text-white
font-semibold
">

{item.title}

</h3>


<span
className={`
px-2
py-1
rounded
border
text-xs
${style.badge}
`}
>

{item.severity}

</span>


</div>



<p className="
text-xs
text-gray-400
mt-1
">

{item.engine}

 · {item.status}

</p>


</div>



<div className="
text-right
text-xs
text-gray-400
">


<div>
Events:
<span className="text-white ml-1">

{
item.timeline.events
??
0
}

</span>

</div>


<div>
Evidence:
<span className="text-white ml-1">

{
item.timeline.evidence_actions
??
0
}

</span>

</div>


</div>


</button>





{
open &&

<div className="
border-t
border-gray-700
p-5
space-y-5
">


{/* LAST EVENT */}

<div className="
bg-gray-900
rounded-lg
p-4
">


<div className="
flex
items-center
gap-2
text-primary-400
mb-2
">

<Clock
className="w-4 h-4"
/>

Last Event

</div>



<p className="
text-white
font-medium
">

{
item.timeline.last_event?.event
??
"No event"
}

</p>


<div className="
grid
md:grid-cols-2
gap-3
mt-3
text-sm
text-gray-400
">


<div className="
flex
gap-2
">

<User className="w-4 h-4"/>

{
item.timeline.last_event?.actor
??
"-"
}

</div>



<div>

{
item.timeline.last_event?.timestamp
??
"-"
}

</div>


</div>


</div>






{/* METRICS */}


<div className="
grid
grid-cols-3
gap-3
">


<div className="
border
border-red-500/30
rounded-lg
p-3
">


<p className="text-xs text-gray-400">

SLA Breach

</p>


<p className="
text-xl
font-bold
text-red-400
">

{
item.timeline.sla_breach
??
0
}

</p>


</div>




<div className="
border
border-blue-500/30
rounded-lg
p-3
">


<p className="text-xs text-gray-400">

Evidence Actions

</p>


<p className="
text-xl
font-bold
text-blue-400
">

{
item.timeline.evidence_actions
??
0
}

</p>


</div>




<div className="
border
border-green-500/30
rounded-lg
p-3
">


<p className="text-xs text-gray-400">

Events

</p>


<p className="
text-xl
font-bold
text-green-400
">

{
item.timeline.events
??
0
}

</p>


</div>



</div>







{/* DECISION */}

{


item.decision?.status

&&

<div className="
flex
gap-3
items-center
text-sm
text-gray-300
">


<ShieldAlert
className="w-4 h-4 text-orange-400"
/>


Decision:

<span className="
text-white
">

{
item.decision.status
}

</span>


{
item.decision.actor

&&

<span className="text-gray-400">

by {item.decision.actor}

</span>

}


</div>


}





{/* RECOMMENDATIONS */}


{

item.recommendations.length>0

&&

<div>

<h4 className="
text-sm
text-white
font-semibold
mb-2
">

Recommendations

</h4>


<div className="
space-y-2
">


{
item.recommendations.map(
(
r:string,
i:number
)=>(


<div

key={i}

className="
flex
gap-2
text-sm
text-gray-400
"

>

<FileCheck
className="
w-4 h-4
text-green-400
"
/>

{r}

</div>


)

)

}


</div>


</div>


}



</div>

}



</div>

);


}

)

}


</div>



</div>

);

}
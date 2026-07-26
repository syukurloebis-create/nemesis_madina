import React from "react";

import {
 Network,
 ShieldAlert,
 GitBranch
} from "lucide-react";


import {
 IntelligenceModel
} from "../../services/intelligenceAdapter";


import GraphEntityExplorer
from "./GraphEntityExplorer";



interface Props {

 intelligence:IntelligenceModel;

}



export default function GraphIntelligence({

 intelligence

}:Props){



const graph =
intelligence?.graph
||
{
 entities:0,
 relationships:0
};



const hubs =
intelligence
?.fraud
?.signals
?.hub_entities
||
[];




const highRisk =
hubs.filter(
x =>
x.risk_level==="HIGH"
).length;



return (

<div
className="
space-y-6
"
>


{/* GRAPH SUMMARY */}


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
items-center
gap-3
mb-6
"
>


<Network
className="
text-purple-400
w-6
h-6
"
/>


<div>

<h2
className="
text-xl
font-bold
text-white
"
>

Graph Intelligence

</h2>


<p
className="
text-sm
text-gray-400
"
>

Entity relationship risk analysis

</p>


</div>


</div>





<div
className="
grid
grid-cols-3
gap-4
"
>



<div
className="
bg-gray-900
rounded-xl
p-5
"
>

<div
className="
flex
gap-2
items-center
text-gray-400
text-sm
"
>

<Network
className="
w-4
"
/>

Entities

</div>


<p
className="
text-3xl
font-bold
text-white
mt-2
"
>

{graph.entities}

</p>


</div>





<div
className="
bg-gray-900
rounded-xl
p-5
"
>

<div
className="
flex
gap-2
items-center
text-gray-400
text-sm
"
>

<GitBranch
className="
w-4
"
/>

Relationships

</div>


<p
className="
text-3xl
font-bold
text-white
mt-2
"
>

{graph.relationships}

</p>


</div>






<div
className="
bg-gray-900
rounded-xl
p-5
"
>


<div
className="
flex
gap-2
items-center
text-gray-400
text-sm
"
>


<ShieldAlert
className="
w-4
text-red-400
"
/>

High Risk Hubs

</div>



<p
className="
text-3xl
font-bold
text-red-400
mt-2
"
>

{highRisk}

</p>



</div>



</div>



</div>







{/* ENTITY DRILL DOWN */}


<GraphEntityExplorer

intelligence={intelligence}

/>



</div>


);


}
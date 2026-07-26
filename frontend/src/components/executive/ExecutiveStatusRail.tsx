import React from "react";

import {
ShieldAlert,
Activity,
Network,
FileCheck
}
from "lucide-react";


export default function ExecutiveStatusRail({

intelligence

}:any){


const risk =
intelligence?.risk ?? {};


const graph =
intelligence?.graph ?? {};


const evidence =
intelligence?.evidence ?? {};



return (

<div className="
bg-[#182235]
border
border-gray-700
rounded-2xl
p-5
">


<div className="
flex
justify-between
items-center
">


<div>

<h1 className="
text-2xl
font-bold
text-white
">

Executive Intelligence Center

</h1>


<p className="
text-gray-400
text-sm
">

AI Fraud & Risk Command Platform

</p>


</div>



<div className="
flex
gap-10
">


<div>

<Activity
className="
text-blue-400
mb-1
"/>

<p className="
text-xs text-gray-400
">

Risk Score

</p>


<b className="
text-white
text-xl
">

{risk.score ?? 0}%

</b>

</div>



<div>

<ShieldAlert
className="
text-red-400
mb-1
"/>

<p className="
text-xs text-gray-400
">

Risk Level

</p>


<b className="
text-red-400
text-xl
">

{risk.level}

</b>

</div>



<div>

<Network
className="
text-purple-400
mb-1
"/>

<p className="
text-xs text-gray-400
">

Entities

</p>


<b className="
text-white
text-xl
">

{graph.entities}

</b>


</div>



<div>

<FileCheck
className="
text-green-400
mb-1
"/>

<p className="
text-xs text-gray-400
">

Evidence

</p>


<b className="
text-green-400
text-xl
">

{evidence.total}

</b>


</div>



</div>


</div>


</div>

);


}
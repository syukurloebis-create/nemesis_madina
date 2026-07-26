import React from "react";
import {
 ShieldCheck,
 AlertTriangle,
 Activity
} from "lucide-react";

import {
 IntelligenceModel
} from "../../services/intelligenceAdapter";


interface Props{
 intelligence:IntelligenceModel;
}


export default function ExecutiveHeader({
 intelligence
}:Props){


const risk =
intelligence?.risk?.level ?? "UNKNOWN";


const score =
intelligence?.risk?.score ?? 0;


const fraud =
intelligence?.fraud?.overall_risk ?? "NORMAL";



return (

<div
className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
flex
justify-between
items-center
"
>


<div>


<div
className="
flex
items-center
gap-3
"
>


<ShieldCheck
className="
text-primary-400
w-8
h-8
"
/>


<div>

<h1
className="
text-2xl
font-bold
text-white
"
>

Executive Intelligence Center

</h1>


<p
className="
text-sm
text-gray-400
"
>

AI Fraud & Risk Command Platform

</p>


</div>


</div>


</div>



<div
className="
grid
grid-cols-3
gap-6
text-center
"
>


<div>

<Activity
className="
mx-auto
text-blue-400
"
/>


<p className="
text-xs
text-gray-400
">

Risk Score

</p>


<p className="
text-xl
font-bold
text-white
">

{score}%

</p>

</div>




<div>

<AlertTriangle
className="
mx-auto
text-red-400
"
/>


<p className="
text-xs
text-gray-400
">

Risk Level

</p>


<p className="
text-xl
font-bold
text-red-400
">

{risk}

</p>


</div>




<div>


<p className="
text-xs
text-gray-400
">

Fraud Engine

</p>


<p className="
text-xl
font-bold
text-orange-400
">

{fraud}

</p>


</div>



</div>


</div>

)

}
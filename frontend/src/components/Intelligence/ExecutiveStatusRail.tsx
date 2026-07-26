import React from "react";

import {
 ShieldAlert,
 Activity,
 Network,
 FileCheck
} from "lucide-react";


import {
 IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props{

 intelligence: IntelligenceModel;

}



export default function ExecutiveStatusRail({

 intelligence

}:Props){



return (

<div className="
bg-dark-card
border
border-dark-border
rounded-2xl
p-6
flex
justify-between
items-center
">


<div>

<h1 className="
text-3xl
font-bold
text-white
">

Executive Intelligence Center

</h1>


<p className="
text-gray-400
mt-1
">

AI Fraud & Risk Command Platform

</p>


</div>



<div className="
flex
gap-10
">


<Metric

icon={<Activity/>}

label="Risk Score"

value={`${intelligence.risk.score}%`}

/>



<Metric

icon={<ShieldAlert/>}

label="Risk Level"

value={intelligence.risk.level}

/>



<Metric

icon={<Network/>}

label="Entities"

value={intelligence.graph.entities}

/>



<Metric

icon={<FileCheck/>}

label="Evidence"

value={intelligence.evidence.total}

/>


</div>



</div>


);

}





function Metric({

icon,

label,

value

}:any){


return (

<div className="
text-center
">


<div className="
text-blue-400
flex
justify-center
mb-2
">

{icon}

</div>


<p className="
text-xs
text-gray-400
">

{label}

</p>


<p className="
text-xl
font-bold
text-white
">

{value}

</p>


</div>

);


}
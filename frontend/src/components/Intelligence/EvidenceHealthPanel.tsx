import React from "react";


import {
ShieldCheck,
AlertTriangle,
FileCheck,
Activity,
Info
}
from "lucide-react";


import {
IntelligenceModel
}
from "../../services/intelligenceAdapter";



interface Props {

 intelligence:IntelligenceModel;

}





const confidenceStyle=(level:string)=>{


switch(level){

case "HIGH":

return "text-green-400 bg-green-500/10 border-green-500/30";


case "MEDIUM":

return "text-yellow-400 bg-yellow-500/10 border-yellow-500/30";


case "LOW":

return "text-red-400 bg-red-500/10 border-red-500/30";


default:

return "text-gray-400 bg-gray-500/10";

}


};







function ScoreBar({

label,

value

}:{

label:string;

value:number;

}){


return (

<div className="
space-y-2
">


<div className="
flex
justify-between
text-sm
">


<span className="
text-gray-400
">

{label}

</span>


<span className="
text-white
font-semibold
">

{value.toFixed(1)}

</span>


</div>




<div className="
h-2
bg-gray-800
rounded-full
overflow-hidden
">


<div

className="
h-full
bg-primary-500
"

style={{

width:`${Math.min(value,100)}%`

}}


/>


</div>



</div>

);


}








export default function EvidenceHealthPanel({

intelligence

}:Props){



const evidence =

intelligence?.evidence;





if(!evidence)

return null;






return (

<div className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
space-y-6
">






{/* HEADER */}



<div className="
flex
justify-between
items-start
">


<div>


<h2 className="
text-xl
font-bold
text-white
flex
items-center
gap-2
">


<ShieldCheck

className="
text-green-400
"/>


Evidence Intelligence


</h2>


<p className="
text-sm
text-gray-400
">

Evidence reliability assessment engine

</p>


</div>







<div

className={`
px-3
py-2
rounded-lg
border
text-sm

${confidenceStyle(
evidence.confidence_level
)}

`}

>


{
evidence.confidence_level
}

CONFIDENCE


</div>



</div>









{/* SCORE SUMMARY */}



<div className="
grid
grid-cols-4
gap-4
">


<div className="
bg-gray-900
rounded-xl
p-4
">


<p className="
text-xs
text-gray-400
">

Evidence Score

</p>


<p className="
text-3xl
font-bold
text-white
">

{
evidence.score
}

</p>


</div>




<div className="
bg-gray-900
rounded-xl
p-4
">


<p className="
text-xs
text-gray-400
">

Total Evidence

</p>


<p className="
text-3xl
font-bold
text-white
">

{
evidence.total
}

</p>


</div>





<div className="
bg-gray-900
rounded-xl
p-4
">


<p className="
text-xs
text-gray-400
">

Verified

</p>


<p className="
text-3xl
font-bold
text-green-400
">

{
evidence.verified
}

</p>


</div>





<div className="
bg-gray-900
rounded-xl
p-4
">


<p className="
text-xs
text-gray-400
">

Rejected

</p>


<p className="
text-3xl
font-bold
text-red-400
">

{
evidence.rejected
}

</p>


</div>


</div>









{/* COMPONENT ANALYSIS */}



<div className="
grid
grid-cols-1
lg:grid-cols-2
gap-5
">





<div className="
border
border-gray-700
rounded-xl
p-5
">


<h3 className="
text-white
font-semibold
mb-4
flex
items-center
gap-2
">


<Activity

className="
w-5
text-blue-400
"/>


Evidence Components


</h3>





<ScoreBar

label="Trust Component"

value={
evidence.components?.trust_component ?? 0
}

/>



<ScoreBar

label="Verification Component"

value={
evidence.components?.verification_component ?? 0
}

/>



<ScoreBar

label="Integrity Component"

value={
evidence.components?.integrity_component ?? 0
}

/>



<ScoreBar

label="Confidence Component"

value={
evidence.components?.confidence_component ?? 0
}

/>



</div>








{/* HEALTH STATUS */}



<div className="
border
border-gray-700
rounded-xl
p-5
space-y-4
">


<h3 className="
text-white
font-semibold
flex
gap-2
items-center
">


<FileCheck

className="
w-5
text-green-400
"/>


Evidence Health


</h3>







<div className="
flex
justify-between
text-sm
">


<span className="
text-gray-400
">

Custody Events

</span>


<span className="
text-white
font-bold
">

{
evidence.custody_events
}

</span>


</div>






<div className="
flex
justify-between
text-sm
">


<span className="
text-gray-400
">

Status

</span>


<span className="
text-green-400
font-bold
">

{
evidence.level
}

</span>


</div>







<div className="
mt-4
p-4
rounded-lg
bg-yellow-500/10
border
border-yellow-500/30
">


<div className="
flex
gap-2
items-start
">


<AlertTriangle

className="
w-5
text-yellow-400
mt-1
"/>



<div>


<p className="
text-xs
text-yellow-300
font-semibold
">

AI Recommendation


</p>


<p className="
text-sm
text-gray-300
mt-1
">

{
evidence.recommendation
}

</p>


</div>



</div>



</div>






</div>



</div>






</div>


);

}
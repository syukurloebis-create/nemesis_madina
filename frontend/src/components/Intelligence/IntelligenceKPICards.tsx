import React from "react";

import {
  IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props {

  data?: IntelligenceModel | null;

  loading?: boolean;

}



const KPI = ({
  title,
  value,
  subtitle,
  icon
}:any)=>{


return (

<div
className="
bg-dark-card
border
border-dark-border
rounded-xl
p-5
hover:border-primary-500
transition
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

<p
className="
text-xs
text-dark-muted
uppercase
tracking-wide
"
>
{title}
</p>



<p
className="
text-3xl
font-bold
text-white
mt-2
"
>
{value}
</p>



<p
className="
text-xs
text-gray-400
mt-1
"
>
{subtitle}
</p>


</div>


<div
className="
text-3xl
"
>
{icon}
</div>


</div>


</div>

)

};





export default function IntelligenceKPICards({

data,

loading=false

}:Props){



if(loading){

return (

<div
className="
grid
grid-cols-1
md:grid-cols-2
lg:grid-cols-4
gap-4
"
>

{
[1,2,3,4].map(i=>(

<div
key={i}
className="
h-32
rounded-xl
bg-gray-800
animate-pulse
"
/>

))
}

</div>

)

}





const cards=[


{

title:"Fraud Risk",

value:
data?.fraud?.overall_risk ?? "NORMAL",

subtitle:
`${data?.fraud?.active_alerts ?? 0} active alerts`,

icon:"🔥"

},



{

title:"Graph Intelligence",

value:
data?.graph?.entities ?? 0,

subtitle:
`${data?.graph?.relationships ?? 0} relationships`,

icon:"🕸️"

},



{

title:"Risk Score",

value:
`${data?.risk?.score ?? 0}%`,

subtitle:
data?.risk?.level ?? "UNKNOWN",

icon:"⚠️"

},



{

title:"Evidence Confidence",

value:
`${data?.evidence?.score ?? 0}%`,

subtitle:
`${data?.evidence?.total ?? 0} evidence items`,

icon:"📂"

}


];




return (

<div
className="
grid
grid-cols-1
md:grid-cols-2
lg:grid-cols-4
gap-4
"
>


{
cards.map(card=>(

<KPI

key={card.title}

{...card}

/>

))
}



</div>

)

}
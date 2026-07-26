import React from "react";


import {
 IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props{

 intelligence: IntelligenceModel;

}



export default function ExecutiveKPIRow({

 intelligence

}:Props){



const cards=[


{

title:"Fraud Risk",

value:
intelligence.fraud.overall_risk,

sub:
`${intelligence.fraud.active_alerts} active alerts`,

color:"text-red-400"

},



{

title:"Critical Findings",

value:
intelligence.findings.critical,

sub:
`${intelligence.findings.total} total findings`,

color:"text-orange-400"

},



{

title:"Evidence Confidence",

value:
`${intelligence.evidence.score}%`,

sub:
`${intelligence.evidence.total} evidence items`,

color:"text-green-400"

},



{

title:"Graph Network",

value:
intelligence.graph.entities,

sub:
`${intelligence.graph.relationships} relationships`,

color:"text-blue-400"

}



];



return (

<div className="
grid
grid-cols-4
gap-5
">


{

cards.map(
(card,index)=>(


<div

key={index}

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-5
">


<p className="
text-sm
text-gray-400
">

{card.title}

</p>



<p className={`
text-3xl
font-bold
mt-2
${card.color}
`}>

{card.value}

</p>



<p className="
text-xs
text-gray-500
mt-2
">

{card.sub}

</p>



</div>


)

)

}



</div>

);


}
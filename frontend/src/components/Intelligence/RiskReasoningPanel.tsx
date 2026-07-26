import React, {
    useState
} from "react";


import {
    Brain,
    ChevronDown,
    ChevronRight,
    ShieldAlert,
    Activity,
    Clock,
    CheckCircle2
} from "lucide-react";


import {
    IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props {

    intelligence: IntelligenceModel;

}



const severityStyle=(severity:string)=>{

    switch(severity){

        case "CRITICAL":
            return "bg-red-500/20 border-red-500/40 text-red-400";


        case "HIGH":
            return "bg-orange-500/20 border-orange-500/40 text-orange-400";


        case "MEDIUM":
            return "bg-yellow-500/20 border-yellow-500/40 text-yellow-400";


        default:
            return "bg-blue-500/20 border-blue-500/40 text-blue-400";
    }

};



export default function RiskReasoningPanel({

    intelligence

}:Props){



const [

expanded,

setExpanded

]=useState<string[]>([]);



const findings =
intelligence?.findings?.findings ?? [];




const toggle=(id:string)=>{


setExpanded(prev=>

prev.includes(id)

?

prev.filter(x=>x!==id)

:

[
...prev,
id
]

);


};





return (

<section
className="
bg-[#182235]
border
border-slate-700
rounded-2xl
p-6
space-y-6
"
>



<header
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
gap-2
items-center
"
>

<Brain
className="
text-purple-400
"
/>

AI Risk Reasoning Engine

</h2>


<p
className="
text-sm
text-slate-400
mt-1
"
>

Explainable fraud intelligence decision chain

</p>


</div>




<div
className="
text-right
"
>


<p
className="
text-xs
text-slate-400
"
>

Risk Level

</p>


<p
className="
text-2xl
font-bold
text-red-400
"
>

{
intelligence.risk.level
}

</p>


</div>



</header>





<div
className="
grid
grid-cols-3
gap-4
"
>


<div
className="
rounded-xl
bg-red-500/10
border
border-red-500/30
p-4
"
>

<p className="text-slate-400 text-sm">
Critical
</p>

<strong className="text-3xl text-red-400">

{
intelligence.findings.critical
}

</strong>


</div>





<div
className="
rounded-xl
bg-orange-500/10
border
border-orange-500/30
p-4
"
>

<p className="text-slate-400 text-sm">
High
</p>

<strong className="text-3xl text-orange-400">

{
intelligence.findings.high
}

</strong>

</div>





<div
className="
rounded-xl
bg-blue-500/10
border
border-blue-500/30
p-4
"
>


<p className="text-slate-400 text-sm">
Total Findings
</p>


<strong className="text-3xl text-blue-400">

{
intelligence.findings.total
}

</strong>


</div>


</div>






<div
className="
space-y-3
"
>


{
findings.map(
(finding:any)=>(


<div
key={finding.id}
className="
border
border-slate-700
rounded-xl
overflow-hidden
"
>


<button

onClick={()=>toggle(finding.id)}

className="
w-full
flex
items-center
gap-3
p-4
hover:bg-slate-800/60
"

>


{

expanded.includes(finding.id)

?

<ChevronDown/>

:

<ChevronRight/>

}



<span
className={`
px-3
py-1
rounded-lg
text-xs
border
${severityStyle(
finding.severity
)}
`}
>

{
finding.severity
}

</span>




<div
className="
flex-1
text-left
"
>

<p
className="
font-semibold
text-white
"
>

{
finding.title
}

</p>


<p
className="
text-xs
text-slate-400
"
>

Engine:

{
finding.engine
}

</p>

</div>


<div
className="
text-right
"
>


<p className="text-xs text-slate-400">
Risk
</p>

<p className="text-white font-bold">
{
finding.risk_score
}
</p>


</div>



</button>






{
expanded.includes(finding.id)

&&


<div
className="
border-t
border-slate-700
p-5
space-y-4
"
>


<div
className="
flex
gap-2
text-slate-300
"
>

<ShieldAlert
className="text-red-400"
/>


{
finding.description
}


</div>





<div
className="
grid
grid-cols-2
gap-4
"
>


<div
className="
bg-slate-900
rounded-lg
p-3
"
>

<p className="text-xs text-slate-400">
Confidence
</p>


<p className="text-white font-bold">

{
finding.confidence
}%

</p>


</div>



<div
className="
bg-slate-900
rounded-lg
p-3
"
>

<p className="text-xs text-slate-400">
Status
</p>


<p className="text-white font-bold">

{
finding.status
}

</p>


</div>


</div>





<div
className="
space-y-2
"
>


{
finding.intelligence?.explanations?.map(
(x:string)=>(


<div
key={x}
className="
flex
gap-2
text-sm
text-slate-300
"
>

<Activity
size={16}
className="text-blue-400"
/>


{x}


</div>


)

)

}


</div>




<div
className="
flex
gap-2
text-xs
text-slate-400
"
>


<Clock size={14}/>

{
new Date(
finding.created_at
).toLocaleString()
}


</div>



</div>


}



</div>


)

)

}



</div>




</section>


);

}
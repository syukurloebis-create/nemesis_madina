import React from "react";


interface Node {

id:string;

name:string;

risk_score?:number;

connections?:number;

pagerank?:number;

}



interface Props {

data:Node[];

height?:number;

className?:string;

onNodeClick?:(node:Node)=>void;

}



export const EnhancedNetworkGraph =({

data=[],

onNodeClick,

className=""

}:Props)=>{


if(!data.length)

return (

<div className="
p-6
text-center
text-gray-400
">

No graph intelligence data

</div>

);



return (

<div

className={`
relative
${className}
`}

>


<div className="
grid
grid-cols-2
md:grid-cols-3
gap-4
">


{
data
.slice(0,12)
.map(
node=>(


<div

key={node.id}

onClick={()=>onNodeClick?.(node)}

className={`
rounded-xl
border
p-4
cursor-pointer
transition
bg-gray-900
${

(node.risk_score??0)>=80

?

"border-red-500/50"

:

(node.risk_score??0)>=50

?

"border-orange-500/50"

:

"border-gray-700"

}
`}

>


<p className="
text-white
font-semibold
truncate
">

{node.name}

</p>



<div className="
mt-2
text-xs
text-gray-400
space-y-1
">


<div>

Risk:
<span className="
text-white
">

{node.risk_score ?? 0}

%

</span>

</div>

<div className="
h-2
bg-gray-700
rounded
overflow-hidden
">

<div
className="
h-full
bg-red-500
"
style={{
width:`${node.risk_score}%`
}}
/>

</div>


<div>

Connections:

<span className="
text-white
">

{node.connections ?? 0}

</span>

</div>



</div>


</div>


)

)

}


</div>


</div>

);

};



export default EnhancedNetworkGraph;
import React from 'react';

import {
Cpu,
Database,
Users,
Link,
AlertTriangle,
Briefcase
}
from 'lucide-react';



interface Props{

strategic:any;

}



export const AIStatusBar:React.FC<Props>=({

strategic

})=>{


const summary =
strategic?.summary || {};


const graph =
strategic?.graph_intelligence || {};



const stats=[

{
label:'ENTITIES',
value:graph.total_entities || 0,
icon:Users
},

{
label:'RELATIONSHIPS',
value:graph.total_relationships || 0,
icon:Link
},


{
label:'COLLUSION',
value:graph.collusion_edges || 0,
icon:AlertTriangle
},


{
label:'CASES',
value:summary.total_cases || 0,
icon:Briefcase
}


];



return (

<header className="bg-dark-card border-b border-dark-border">

<div className="p-4">


<div className="flex justify-between flex-wrap gap-4">


<div className="flex items-center gap-2">

<Cpu className="text-blue-400"/>

<h1 className="text-xl font-bold">

NEMESIS AI COMMAND CENTER

</h1>


</div>



<div className="flex gap-3">


<span className="text-green-400">

● SYSTEM ACTIVE

</span>


<span className="text-blue-400">

● AI ONLINE

</span>


</div>


</div>



<div className="flex gap-6 mt-4 flex-wrap">


{
stats.map((s,i)=>{

const Icon=s.icon;


return (

<div key={i}
className="flex gap-2 items-center"
>

<Icon size={18}/>

<div>

<div className="font-bold">

{s.value}

</div>


<div className="text-xs text-gray-400">

{s.label}

</div>


</div>


</div>

)

})
}


</div>


</div>

</header>

);

};


export default AIStatusBar;
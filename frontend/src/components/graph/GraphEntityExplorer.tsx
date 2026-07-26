import React, {
useMemo,
useState
} from "react";


import {
Search,
Building2,
ShieldAlert,
Network,
GitBranch,
Package,
Activity,
ChevronRight
} from "lucide-react";


import {
IntelligenceModel
} from "../../services/intelligenceAdapter";



interface Props {

intelligence:IntelligenceModel;

}


import {
fetchEntityNetwork
}
from "../../services/graphIntelligenceApi";


const loadEntityNetwork = async(
 entity:string
)=>{

 try{

 const data =
 await fetchEntityNetwork(entity);


 setNetwork(data);


 }
 catch(error){

 console.error(
 "Entity network failed",
 error
 );

 }

};


const riskBadge=(level:string)=>{


switch(level){


case "HIGH":

return `
bg-red-500/20
text-red-400
border-red-500/40
`;


case "MEDIUM":

return `
bg-yellow-500/20
text-yellow-400
border-yellow-500/40
`;


default:

return `
bg-blue-500/20
text-blue-400
border-blue-500/40
`;

}

};





export default function GraphEntityExplorer({

intelligence

}:Props){



const [
search,
setSearch
]=useState("");



const [
selected,
setSelected
]=useState<any|null>(null);





const hubs =

intelligence
?.fraud
?.signals
?.hub_entities
??

[];




const sharedPackages =

intelligence
?.fraud
?.signals
?.shared_package_patterns
??

[];




const methodPatterns =

intelligence
?.fraud
?.signals
?.method_similarity_patterns
??

[];





const entities = useMemo(()=>{


return hubs.filter(
(entity:any)=>

entity.name
.toLowerCase()
.includes(
search.toLowerCase()
)

);


},[
hubs,
search
]);






const entityPackages = useMemo(()=>{


if(!selected)
return [];


return sharedPackages.filter(
(item:any)=>

item.source===selected.name
||
item.target===selected.name

);


},[
selected,
sharedPackages
]);






const entityMethods = useMemo(()=>{


if(!selected)
return [];


return methodPatterns.filter(
(item:any)=>

item.source===selected.name
||
item.target===selected.name

);


},[
selected,
methodPatterns
]);







return (

<div
className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
space-y-6
"
>



{/* HEADER */}


<div
className="
flex
justify-between
items-start
"
>


<div>


<div
className="
flex
gap-2
items-center
"
>


<Network
className="
text-purple-400
"
/>


<h2
className="
text-xl
font-bold
text-white
"
>

Entity Relationship Explorer

</h2>


</div>



<p
className="
text-sm
text-gray-400
mt-1
"
>

Hub entity investigation from Graph Intelligence

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
text-gray-400
"
>

Hub Entities

</p>


<p
className="
text-2xl
font-bold
text-white
"
>

{hubs.length}

</p>


</div>



</div>








{/* SEARCH */}


<div
className="
flex
items-center
gap-3
bg-gray-900
rounded-lg
px-4
py-3
"
>


<Search
className="
w-4
text-gray-400
"
/>


<input

value={search}

onChange={
e=>
setSearch(
e.target.value
)
}

placeholder="
Search vendor / entity...
"

className="
bg-transparent
outline-none
text-white
w-full
"

/>


</div>









<div
className="
grid
grid-cols-1
xl:grid-cols-3
gap-6
"
>





{/* ENTITY LIST */}


<div
className="
xl:col-span-2
space-y-3
"
>


<h3
className="
text-white
font-semibold
flex
gap-2
items-center
"
>

<Building2
className="
w-4
text-gray-400
"
/>

Risk Hub Ranking

</h3>





<div
className="
grid
md:grid-cols-2
gap-3
"
>


{

entities
.slice(
0,
20
)
.map(
(entity:any)=>(


<button

key={entity.name}

onClick={()=>
setSelected(entity)
}

className="
text-left
bg-gray-900
border
border-gray-700
rounded-xl
p-4
hover:border-purple-400
transition
"

>


<div
className="
flex
justify-between
gap-2
"
>


<span
className="
text-white
font-semibold
truncate
"
>

{entity.name}

</span>



<ChevronRight
className="
w-4
text-gray-500
"
/>


</div>





<div
className="
mt-3
flex
gap-2
flex-wrap
"
>


<span
className={`
text-xs
px-2
py-1
rounded
border
${riskBadge(
entity.risk_level
)}
`}
>

{entity.risk_level}

</span>



<span
className="
text-xs
text-gray-400
"
>

Degree:

<b
className="
text-white
"
>
{entity.degree}
</b>

</span>



<span
className="
text-xs
text-gray-400
"
>

Weight:

<b
className="
text-white
"
>

{
entity.avg_weight
.toFixed(2)
}

</b>

</span>



</div>




</button>


)

)

}



</div>



</div>










{/* DETAIL */}


<div
className="
bg-gray-900
rounded-xl
border
border-gray-700
p-5
"
>


{
selected

?

<>


<div
className="
flex
gap-2
items-center
mb-5
"
>


<ShieldAlert
className="
text-red-400
"
/>


<h3
className="
text-white
font-bold
"
>

{selected.name}

</h3>


</div>




<div
className="
space-y-4
"
>


<div>

<p
className="
text-xs
text-gray-400
"
>
Degree
</p>


<p
className="
text-2xl
font-bold
text-white
"
>

{selected.degree}

</p>

</div>




<div>

<p
className="
text-xs
text-gray-400
"
>
PageRank
</p>


<p
className="
text-white
"
>

{
selected.pagerank
}

</p>


</div>




<div>

<p
className="
text-xs
text-gray-400
"
>
Average Weight
</p>


<p
className="
text-white
"
>

{
selected.avg_weight
.toFixed(2)
}

</p>


</div>


</div>





</>


:

<div
className="
text-center
text-gray-500
py-10
"
>


<Network
className="
mx-auto
mb-3
"
/>


Select entity


</div>

}


</div>



</div>









{/* PATTERN ANALYSIS */}


{
selected

&&


<div
className="
grid
md:grid-cols-2
gap-5
"
>


{/* PACKAGE */}


<div
className="
border
border-gray-700
rounded-xl
p-5
"
>


<div
className="
flex
gap-2
items-center
text-white
font-semibold
mb-3
"
>


<Package
className="
text-orange-400
"
/>


Shared Package Pattern

</div>


{

entityPackages.length===0

?

<p
className="
text-gray-500
text-sm
"
>
No package relation
</p>


:

entityPackages.map(
(item:any,index:number)=>(

<div
key={index}
className="
text-sm
text-gray-300
mb-2
"
>

{item.source}

→

{item.target}


<span
className="
text-orange-400
ml-2
"
>

{item.weight}%

</span>


</div>

)

)

}


</div>








{/* METHOD */}


<div
className="
border
border-gray-700
rounded-xl
p-5
"
>


<div
className="
flex
gap-2
items-center
text-white
font-semibold
mb-3
"
>


<Activity
className="
text-blue-400
"
/>


Method Similarity

</div>




{

entityMethods.length===0

?

<p
className="
text-gray-500
text-sm
"
>

No similarity relation

</p>


:

entityMethods.map(
(item:any,index:number)=>(


<div
key={index}
className="
text-sm
text-gray-300
mb-2
"
>

{item.source}

→

{item.target}


<span
className="
text-blue-400
ml-2
"
>

{item.weight}%

</span>


</div>


)

)


}



</div>




</div>


}



</div>


);

}
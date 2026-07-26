import React, {
useState
}
from "react";


import {
Layers,
Network,
GitCompare,
ChevronDown,
ChevronRight,
AlertTriangle
}
from "lucide-react";


import {
IntelligenceModel
}
from "../../services/intelligenceAdapter";



interface Props {

intelligence:IntelligenceModel;

}



type Section =
"cluster"
|
"package"
|
"method";





const riskStyle=(level:string)=>{


switch(level){

case "HIGH":

return "text-red-400 bg-red-500/10 border-red-500/30";


case "MEDIUM":

return "text-yellow-400 bg-yellow-500/10 border-yellow-500/30";


default:

return "text-blue-400 bg-blue-500/10 border-blue-500/30";

}


};







export default function FraudSignalExplorer({

intelligence

}:Props){



const [

active,

setActive

]=useState<Section>("cluster");




const [

expanded,

setExpanded

]=useState<number|null>(null);






const signals =

intelligence
?.fraud
?.signals
??
{};




const clusters =

signals.high_risk_clusters
??
[];




const packages =

signals.shared_package_patterns
??
[];




const methods =

signals.method_similarity_patterns
??
[];






const toggle=(id:number)=>{


setExpanded(

expanded===id
?
null
:
id

);


};







return (

<div className="
bg-dark-card
border
border-dark-border
rounded-xl
p-6
space-y-6
">





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


<AlertTriangle

className="
text-orange-400
"/>


Fraud Signal Explorer


</h2>



<p className="
text-sm
text-gray-400
">

Fraud intelligence pattern analysis

</p>


</div>




<div className="
text-right
">


<p className="
text-xs
text-gray-400
">

Total Signals

</p>


<p className="
text-2xl
font-bold
text-white
">

{
clusters.length
+
packages.length
+
methods.length

}

</p>


</div>


</div>







{/* ENGINE SELECTOR */}


<div className="
grid
grid-cols-3
gap-3
">



<button

onClick={()=>setActive("cluster")}

className={`

p-4
rounded-lg
border

${
active==="cluster"

?
"border-primary-500 bg-primary-500/10"

:
"border-gray-700"

}

`}

>


<Layers
className="
w-5
text-purple-400
mb-2
"/>


<p className="
text-white
font-semibold
">

Risk Cluster

</p>


<p className="
text-xs
text-gray-400
">

{
clusters.length
}

clusters

</p>


</button>







<button

onClick={()=>setActive("package")}

className={`

p-4
rounded-lg
border

${
active==="package"

?
"border-primary-500 bg-primary-500/10"

:
"border-gray-700"

}

`}

>


<Network

className="
w-5
text-green-400
mb-2
"/>


<p className="
text-white
font-semibold
">

Shared Package

</p>


<p className="
text-xs
text-gray-400
">

{
packages.length
}

patterns

</p>


</button>








<button

onClick={()=>setActive("method")}

className={`

p-4
rounded-lg
border

${
active==="method"

?
"border-primary-500 bg-primary-500/10"

:
"border-gray-700"

}

`}

>


<GitCompare

className="
w-5
text-blue-400
mb-2
"/>


<p className="
text-white
font-semibold
">

Method Similarity

</p>


<p className="
text-xs
text-gray-400
">

{
methods.length
}

patterns

</p>


</button>



</div>









{/* CONTENT */}



<div className="
space-y-3
">



{

active==="cluster"

&&

clusters.map(

(cluster:any,index:number)=>(


<div

key={index}

className="
border
border-gray-700
rounded-lg
overflow-hidden
">


<button

className="
w-full
p-4
flex
justify-between
items-center
text-left
"

onClick={()=>toggle(index)}

>


<div>


<p className="
text-white
font-semibold
">

Cluster #{cluster.cluster_id}

</p>


<div className="
text-xs
text-gray-400
mt-1
flex
gap-3
">


<span>

Members:

{cluster.member_count}

</span>


<span>

Weight:

{
cluster.avg_weight.toFixed(2)

}

</span>


</div>


</div>




<div className="
flex
items-center
gap-3
">


<span

className={`
px-2
py-1
rounded
border
text-xs

${riskStyle(cluster.risk_level)}

`}

>

{
cluster.risk_level
}

</span>


{

expanded===index

?

<ChevronDown/>

:

<ChevronRight/>

}


</div>


</button>




{

expanded===index

&&

<div className="
p-4
border-t
border-gray-700
text-sm
text-gray-300
">


<p>

Average PageRank:

{
cluster.avg_pagerank.toFixed(6)

}

</p>


</div>

}



</div>


)

)

}









{

active==="package"

&&

packages.map(

(item:any,index:number)=>(


<div

key={index}

className="
border
border-gray-700
rounded-lg
p-4
">


<div className="
flex
justify-between
">


<div>

<p className="
text-white
font-medium
">

{item.source}

</p>


<p className="
text-gray-500
text-xs
">

↓

</p>


<p className="
text-white
font-medium
">

{item.target}

</p>


</div>



<div className="
text-right
">


<p className="
text-yellow-400
font-bold
">

{item.weight}

</p>


<p className="
text-xs
text-gray-400
">

Shared Package

</p>


</div>


</div>


</div>


)

)

}









{

active==="method"

&&

methods.map(

(item:any,index:number)=>(


<div

key={index}

className="
border
border-gray-700
rounded-lg
p-4
">


<div className="
flex
justify-between
">


<div>


<p className="
text-white
">

{item.source}

</p>


<p className="
text-gray-500
text-xs
">

similar pattern

</p>


<p className="
text-white
">

{item.target}

</p>


</div>



<div>

<p className="
text-blue-400
font-bold
">

{item.weight}

</p>


</div>


</div>


</div>


)

)

}



</div>






</div>

);


}
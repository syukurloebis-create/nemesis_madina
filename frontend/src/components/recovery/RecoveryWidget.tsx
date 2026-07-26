import React from 'react';


interface Props{

data:any;

onOpen:()=>void;

}


export default function RecoveryWidget({
data,
onOpen
}:Props){


const recovery =
data?.recovery;



return(

<div
className="
bg-gray-800
border
border-gray-700
rounded-xl
p-5
"
>


<div className="
flex
justify-between
items-center
">


<div>


<h3 className="
text-white
font-semibold
">
Recovery Intelligence
</h3>


<p className="
text-gray-400
text-sm
">
Pemulihan kerugian dan asset recovery
</p>


</div>


<button
onClick={onOpen}
className="
px-3
py-2
bg-blue-600
text-white
rounded-lg
text-sm
"
>

Open

</button>


</div>



<div className="
grid
grid-cols-3
gap-4
mt-5
">


<div>

<p className="text-gray-400 text-xs">
Recovered
</p>

<p className="text-2xl text-green-400">
{recovery?.recovered ?? 0}
</p>

</div>


<div>

<p className="text-gray-400 text-xs">
Pending
</p>

<p className="text-2xl text-yellow-400">
{recovery?.pending ?? 0}
</p>

</div>


<div>

<p className="text-gray-400 text-xs">
Rate
</p>

<p className="text-2xl text-white">
{recovery?.recovery_rate ?? 0}%
</p>

</div>


</div>


</div>

)


}
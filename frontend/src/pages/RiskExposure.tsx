import React from 'react';


export default function RiskExposure(){


return (

<div className="min-h-screen bg-gray-900 p-6">


<h1 className="text-3xl font-bold text-white">
💰 Risk Exposure Analytics
</h1>


<div className="grid grid-cols-3 gap-5 mt-8">


<Card
title="Financial Exposure"
value="Rp 0"
/>


<Card
title="Critical Exposure"
value="3"
/>


<Card
title="Recovery Potential"
value="82%"
/>



</div>


</div>

)

}



function Card(
{
title,
value
}:{
title:string;
value:string;
}){

return (

<div className="
bg-gray-800
border
border-gray-700
rounded-xl
p-6
">


<p className="text-gray-400">
{title}
</p>


<h2 className="text-3xl text-white font-bold mt-3">
{value}
</h2>


</div>

)

}
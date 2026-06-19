import React from 'react';

import {
Briefcase,
AlertTriangle,
DollarSign,
ShieldCheck,
TrendingUp
}
from 'lucide-react';



interface Props{

strategic:any;

}



export const IntelligenceKPICards:React.FC<Props>=({

strategic

})=>{


const summary =
strategic?.summary || {};



const cards=[


{

label:'TOTAL CASES',

value:summary.total_cases || 0,

icon:Briefcase

},


{

label:'HIGH RISK',

value:summary.high_risk_cases || 0,

icon:AlertTriangle

},


{

label:'LOSS',

value:
`Rp ${summary.total_loss?.toLocaleString() || 0}`,

icon:DollarSign

},


{

label:'RECOVERED',

value:
`Rp ${summary.total_recovered?.toLocaleString() || 0}`,

icon:ShieldCheck

}


];



return (

<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">


{

cards.map((c,i)=>{


const Icon=c.icon;


return (

<div

key={i}

className="
bg-dark-card
border
border-dark-border
rounded-xl
p-4
"

>


<div className="flex justify-between">


<div>

<p className="text-xs text-gray-400">

{c.label}

</p>


<h2 className="text-2xl font-bold">

{c.value}

</h2>


</div>


<Icon/>

</div>


</div>

)

})

}


</div>

);

};


export default IntelligenceKPICards;
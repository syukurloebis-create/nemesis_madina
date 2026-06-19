import React from 'react';

import {
useDashboardData
}
from '../../hooks/useDashboardData';


import {
ErrorBoundary
}
from '../../components/common/ErrorBoundary';


import {
AIStatusBar
}
from '../../components/intelligence/AIStatusBar';


import {
AIRiskScore
}
from '../../components/intelligence/AIRiskScore';


import {
IntelligenceKPICards
}
from '../../components/intelligence/IntelligenceKPICards';


import {
EnhancedNetworkGraph
}
from '../../components/network/EnhancedNetworkGraph';



interface Props{

caseId:string;

evidenceId:string;

}



export const DashboardMenu:React.FC<Props>=({

caseId

})=>{


const {
loading,
error,
data

}=useDashboardData(caseId);



if(loading)

return (

<div className="flex justify-center h-64 items-center">

Loading NEMESIS AI Intelligence...

</div>

);



if(error)

return (

<div className="bg-red-500/10 p-6 rounded-xl text-red-400">

{error}

</div>

);



const strategic=data.strategic;



return (

<div className="space-y-6">


<AIStatusBar
strategic={strategic}
/>



<div className="grid grid-cols-1 lg:grid-cols-5 gap-4">


<div>

<AIRiskScore

riskScore={
strategic?.summary?.high_risk_cases || 0
}

/>

</div>



<div className="lg:col-span-4">

<IntelligenceKPICards

strategic={strategic}

/>

</div>


</div>



<ErrorBoundary
fallback={
<div>
Graph Error
</div>
}
>

<EnhancedNetworkGraph

actors={data.keyActors}

height={450}

/>

</ErrorBoundary>



</div>

);

};


export default DashboardMenu;
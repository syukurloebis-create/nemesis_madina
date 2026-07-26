// Dashboard.tsx
// Executive Intelligence Command Center V7

import React, {
  useState,
  useCallback
} from "react";

import {
  ToastContainer,
  toast
} from "react-toastify";


import {
  useNavigate
} from "react-router-dom";


import {
  MainLayout
} from "../components/layout/MainLayout";


import {
  useIntelligenceDashboard
} from "../hooks/useIntelligenceDashboard";


import {
  normalizeIntelligence
} from "../services/intelligenceAdapter";



import ExecutiveStatusRail
from "../components/executive/ExecutiveStatusRail";


import ExecutiveKPIRow
from "../components/intelligence/ExecutiveKPIRow";


import IntelligenceTabs
from "../components/intelligence/IntelligenceTabs";


import "react-toastify/dist/ReactToastify.css";




const CASE_ID =
"446e216d-eb0e-487e-8e6b-ec943468ea20";


const USER_ID =
"user-123";




export default function Dashboard(){



const navigate =
useNavigate();





// =================================================
// BACKEND SINGLE SOURCE OF TRUTH
// =================================================


const {

data,

loading,

error,

refresh

}

=

useIntelligenceDashboard(
CASE_ID
);






// =================================================
// NORMALIZE BACKEND RESPONSE
// =================================================


const intelligence =

data

?

normalizeIntelligence(data)

:

null;






// =================================================
// TAB STATE
// =================================================


const [

activeTab,

setActiveTab

]

=

useState(
"overview"
);







// =================================================
// ACTION BUS
// =================================================


const handleAction =

useCallback(

(action:string)=>{


console.log(
"[Dashboard Action]",
action
);



toast.info(action);




const routes:Record<string,string>={


alerts:
"/alerts",


investigation:
"/investigation",


recovery:
"/recovery",


procurement:
"/procurement",


decisions:
"/decisions"


};



if(routes[action]){


navigate(
routes[action]
);


}



const tabMap:Record<string,string>={


risk:
"risk",


network:
"network",


signals:
"signals",


evidence:
"evidence",


timeline:
"timeline",


investigation:
"investigation",


recovery:
"recovery",


decision:
"decision"


};



if(tabMap[action]){


setActiveTab(
tabMap[action]
);


}



},

[navigate]

);







// =================================================
// LOADING STATE
// =================================================


if(loading){


return (

<div

className="
min-h-screen
bg-[#080f1d]
flex
items-center
justify-center
text-white
"

>


<div
className="
text-center
space-y-4
"
>


<div
className="
w-12
h-12
mx-auto
rounded-full
border-4
border-primary-500
border-t-transparent
animate-spin
"
/>



<p
className="
text-gray-400
"
>

Loading Intelligence Command Center...

</p>



</div>


</div>

);


}








// =================================================
// ERROR STATE
// =================================================


if(error){


return (

<div

className="
m-10
rounded-xl
border
border-red-500
bg-red-900/20
p-6
text-red-300
"

>


<h2
className="
text-xl
font-bold
mb-3
"
>

Intelligence Engine Failure

</h2>


<p>

{error}

</p>


<button

onClick={refresh}

className="
mt-4
px-4
py-2
bg-red-600
rounded-lg
text-white
"

>

Retry

</button>



</div>

);


}








if(!intelligence){


return (

<div

className="
p-10
text-center
text-gray-400
"

>

No Intelligence Data

</div>

);


}









return (

<>


<ToastContainer

position="top-right"

theme="dark"

autoClose={2500}

/>





<MainLayout


activeTab={activeTab}


onTabChange={setActiveTab}


>



<div

className="
space-y-6
"

>





{/* =================================================
EXECUTIVE HEADER
================================================= */}



<ExecutiveStatusRail


intelligence={intelligence}


/>






{/* =================================================
EXECUTIVE KPI SUMMARY
================================================= */}



<ExecutiveKPIRow


intelligence={intelligence}


/>






{/* =================================================
INTELLIGENCE MODULE CONTROLLER
================================================= */}



<IntelligenceTabs


intelligence={intelligence}


activeTab={activeTab}


setActiveTab={setActiveTab}


caseId={CASE_ID}


userId={USER_ID}


onAction={handleAction}


/>





</div>



</MainLayout>




</>

);


}
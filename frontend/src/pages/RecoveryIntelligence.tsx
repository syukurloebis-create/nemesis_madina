import React, { useEffect, useState } from 'react';
import {
  CheckCircle,
  Clock,
  DollarSign,
  ShieldAlert
} from 'lucide-react';


interface RecoveryStats {
  cases:number;
  recovered:number;
  pending:number;
}


export default function RecoveryIntelligence(){

  const [stats,setStats] = useState<RecoveryStats>({
    cases:0,
    recovered:0,
    pending:0
  });


  useEffect(()=>{

    // sementara fallback intelligence engine
    // nanti diganti API recovery endpoint

    setStats({
      cases:24,
      recovered:12400000000,
      pending:8
    });

  },[]);



  const currency =
    new Intl.NumberFormat(
      'id-ID',
      {
        style:'currency',
        currency:'IDR',
        maximumFractionDigits:0
      }
    );



  return (

    <div className="min-h-screen bg-gray-900 p-6">


      <div className="mb-8">

        <h1 className="text-3xl font-bold text-white">
          Recovery Intelligence Center
        </h1>

        <p className="text-gray-400 mt-2">
          AI assisted recovery monitoring,
          remediation tracking and financial recovery analysis
        </p>

      </div>



      <div className="grid grid-cols-3 gap-5">


        <KPI
          icon={<ShieldAlert/>}
          title="Recovery Cases"
          value={stats.cases.toString()}
        />


        <KPI
          icon={<DollarSign/>}
          title="Recovered Value"
          value={currency.format(stats.recovered)}
        />


        <KPI
          icon={<Clock/>}
          title="Pending Actions"
          value={stats.pending.toString()}
        />


      </div>



      <div className="mt-8 bg-gray-800 rounded-lg p-6">

        <h2 className="text-xl font-bold text-white mb-5">
          Recovery Decision Timeline
        </h2>


        <div className="space-y-4">


          <Timeline
            title="Fraud Case Identified"
            status="Completed"
          />


          <Timeline
            title="Asset Recovery Analysis"
            status="Running"
          />


          <Timeline
            title="Remediation Execution"
            status="Pending"
          />


        </div>


      </div>



    </div>

  );

}



function KPI(
{
 icon,
 title,
 value
}:{
 icon:React.ReactNode;
 title:string;
 value:string;
}){

return (

<div className="
bg-gray-800
border border-gray-700
rounded-lg
p-5
">

<div className="flex gap-3 items-center text-gray-400">

{icon}

<span>
{title}
</span>

</div>


<div className="text-3xl font-bold text-white mt-3">

{value}

</div>


</div>

);

}



function Timeline(
{
 title,
 status
}:{
 title:string;
 status:string;
}){


return (

<div className="
flex
justify-between
bg-gray-900
rounded
p-4
">

<span className="text-white">
{title}
</span>


<span className="
text-sm
text-blue-400
flex
gap-2
items-center
">

<CheckCircle size={16}/>

{status}

</span>


</div>

);

}
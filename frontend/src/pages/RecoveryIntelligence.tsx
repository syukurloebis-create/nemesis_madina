import React from "react";
import {useIntelligenceDashboard} from "../hooks/useIntelligenceDashboard";


export default function RecoveryIntelligence(){

 const {
   data,
   loading
 } = useIntelligenceDashboard();


 if(loading)
 return <div>Loading recovery intelligence...</div>


 const recovery=data?.recovery;


 return (

 <div className="p-6">

 <h1 className="text-2xl font-bold">
 Recovery Intelligence
 </h1>


 <div className="grid grid-cols-3 gap-4 mt-6">


 <Card
 title="Recovery Status"
 value={recovery?.status}
 />


 <Card
 title="Progress"
 value={`${recovery?.progress}%`}
 />


 <Card
 title="Recommendations"
 value={recovery?.recommendations?.length}
 />


 </div>

 </div>

 )

}
import {
 useCallback,
 useEffect,
 useState
} from "react";


import {
 fetchIntelligenceDashboard,
 IntelligenceDashboard
} from "../services/dashboardIntelligenceApi";



export function useIntelligenceDashboard(
 caseId?:string
){

const [data,setData]=
useState<IntelligenceDashboard|null>(null);


const [loading,setLoading]=
useState(true);


const [error,setError]=
useState<string|null>(null);



const load = useCallback(async()=>{


if(!caseId){

 setLoading(false);

 return;

}



try{


setLoading(true);

setError(null);



const result =
 await fetchIntelligenceDashboard(caseId);



setData(result);



}
catch(e:any){


setError(
 e?.message ??
 "Failed loading intelligence dashboard"
);


}
finally{


setLoading(false);


}


},[caseId]);



useEffect(()=>{


if(!caseId)
 return;



load();



const timer =
setInterval(
 load,
 30000
);



return ()=>{

clearInterval(timer);

};



},[load,caseId]);



return {

 data,

 loading,

 error,

 refresh:load

};


}



export default useIntelligenceDashboard;
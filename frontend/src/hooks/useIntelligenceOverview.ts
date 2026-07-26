import {
    useCallback,
    useEffect,
    useState
} from "react";


import {
    fetchIntelligenceOverview,
    IntelligenceOverviewResponse
}
from "../services/dashboardIntelligenceApi";



export function useIntelligenceOverview(){


const [data,setData]=
useState<
 IntelligenceOverviewResponse["overview"]
|null>(null);



const [loading,setLoading]=
useState(true);



const [error,setError]=
useState<string|null>(null);



const load =
useCallback(async()=>{


try{


if(!data){

    setLoading(true);

}


setError(null);



const response =
 await fetchIntelligenceOverview();



setData(
 response.overview
);



}
catch(err){


setError(

 err instanceof Error
 ?
 err.message
 :
 "Failed loading intelligence overview"

);


}
finally{


setLoading(false);


}


},[data]);




useEffect(()=>{


load();



const interval =
setInterval(
 load,
 30000
);



return ()=>{

clearInterval(interval);

};



},[load]);




return {

 data,

 loading,

 error,

 refresh:load

};


}



export default useIntelligenceOverview;
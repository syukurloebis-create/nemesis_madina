import {useEffect,useState} from 'react';
import dashboardApi from '../services/dashboardApi';


export interface DashboardData {

  strategic:any;

  keyActors:any[];

}


const emptyData:DashboardData={
  strategic:null,
  keyActors:[]
};



export const useDashboardData=(caseId:string)=>{


const [loading,setLoading]=useState(true);

const [error,setError]=useState<string|null>(null);

const [data,setData]=useState<DashboardData>(emptyData);



useEffect(()=>{


const load=async()=>{


try{


setLoading(true);
setError(null);



const results=
await Promise.allSettled([

 dashboardApi.getStrategicDashboard(),

 dashboardApi.getKeyActors()

]);



const strategicResult=results[0];

const actorsResult=results[1];



const strategic =
strategicResult.status==='fulfilled'
?
strategicResult.value.data
:
null;



const keyActors =
actorsResult.status==='fulfilled'
?
actorsResult.value.data?.key_actors || []
:
[];



setData({

 strategic,

 keyActors

});



if(!strategic && keyActors.length===0)
{
 setError(
  'Dashboard intelligence data unavailable'
 );
}



}
catch(e){

console.error(
'Dashboard loading error',
e
);

setError(
'Failed loading dashboard'
);

}

finally{

setLoading(false);

}


};



load();


},[caseId]);



return {

loading,
error,
data

};

};


export default useDashboardData;
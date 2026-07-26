import {api} from "./api";


export async function fetchEntityNetwork(
 entity:string
){

 const response =
 await api.get(
 `/dashboard/intelligence/entities/${encodeURIComponent(entity)}`
 );


 return response.data;

}
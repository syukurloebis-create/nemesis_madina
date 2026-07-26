import apiClient from "./api/client";


export interface ProcurementSummary {
 totalCases:number;
 totalVendors:number;
 totalValue:number;
 highRiskVendors:number;
 integrityScore:number;
 monthlyTrend:any[];
}


export interface CollusionPattern {
 id:string;
 severity:string;
 type:string;
 confidence:number;
 description:string;
 entities:any[];
}


export const procurementApi = {


getSummary(){
 return apiClient.get('/api/v1/procurement/summary')
},


getCollusionPatterns(){
 return apiClient.get('/api/v1/procurement/collusion-patterns')
},


getRUPStats(){
 return apiClient.get('/api/v1/rup/stats')
},


getSuspicious(){
 return apiClient.get('/api/v1/procurement/vendors/suspicious')
},


getPackages(){
 return apiClient.get('/api/v1/procurement/packages')
},


getStats(){
 return apiClient.get('/api/v1/procurement/stats')
}


};


export const procurementService = procurementApi;

export default procurementApi;
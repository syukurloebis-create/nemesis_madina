import { api } from './api';


export interface IntelligenceOverview {

    risk_summary:{
        critical:number;
        high:number;
        medium:number;
        low:number;
    };


    investigation_health:{
        pending:number;
        confirmed:number;
        rejected:number;
    };


    evidence_health:{
        total_evidence:number;
        average_confidence:number;
    };


    sla_health:{
        breached:number;
        compliant:number;
    };


    top_risk_findings:Array<{

        finding_id:string;

        title:string;

        score:number;

        level:string;

    }>;

}



export interface IntelligenceOverviewResponse {

    overview: IntelligenceOverview;

}



export async function fetchIntelligenceOverview(){

    const response =
        await api.get<IntelligenceOverviewResponse>(
            '/dashboard/intelligence/overview'
        );


    return response.data;

}
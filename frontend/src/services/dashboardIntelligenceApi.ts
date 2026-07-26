import { api } from './api';


export interface FraudSignals {
    high_risk_clusters:any[];
    hub_entities:any[];
    shared_package_patterns:any[];
    method_similarity_patterns:any[];
}

export interface IntelligenceDashboard {


case_id:string;



fraud:{

 overall_risk:string;

 active_alerts:number;

 high_confidence:number;

 signals?:any;

};



graph:{

 entities:number;

 relationships:number;

};



risk:{

 score:number;

 level:string;

 case_status:string;

 engine:string;

};



evidence:{

 score:number;

 level:string;

 total:number;

 verified:number;

 rejected:number;

 pending:number;

 confidence_level:string;

};



findings:{

 total:number;

 critical:number;

 high:number;

 medium:number;

 findings:any[];

};



recovery?:{

 status:string;

 progress:number;

 recoverable_amount:number;

};



procurement?:{

 vendors:number;

 risk_score:number;

 alerts:number;

};



}



export async function fetchIntelligenceDashboard(
    caseId:string
):Promise<IntelligenceDashboard>{


    const response =
        await api.get<IntelligenceDashboard>(
            `/dashboard/intelligence/cases/${caseId}`
        );


    return response.data;

}


export interface IntelligenceOverviewResponse {


    overview:{

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

    };

}



export async function fetchIntelligenceOverview(){

    const response =
        await api.get<IntelligenceOverviewResponse>(
            "/dashboard/intelligence/overview"
        );


    return response.data;

}
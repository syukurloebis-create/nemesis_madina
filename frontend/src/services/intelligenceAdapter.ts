import {
    IntelligenceDashboard
} from "./dashboardIntelligenceApi";



/**
 * =====================================================
 * NEMESIS INTELLIGENCE MODEL
 * Backend Native Mapping
 * =====================================================
 */


export interface IntelligenceModel {

    case_id:string;


    fraud:{

        overall_risk:string;

        active_alerts:number;

        high_confidence:number;

        signals:{

            high_risk_clusters:any[];

            hub_entities:any[];

            shared_package_patterns:any[];

            method_similarity_patterns:any[];

        };

    };


    risk:{

        score:number;

        level:string;

        case_status:string;

        engine:string;

    };


    graph:{

        entities:number;

        relationships:number;

    };


    evidence:{

        score:number;

        level:string;

        total:number;

        verified:number;

        rejected:number;

        pending:number;

        custody_events:number;

        confidence_level:string;

        recommendation:string;

        components?:any;

    };


    findings:{

        total:number;

        critical:number;

        high:number;

        medium:number;

        findings:any[];

    };


}





/**
 * =====================================================
 * NORMALIZER
 * Backend Passthrough
 * =====================================================
 */


export function normalizeIntelligence(

    data?:IntelligenceDashboard|null

):IntelligenceModel{


if(!data){

return {

case_id:"",


fraud:{
overall_risk:"UNKNOWN",
active_alerts:0,
high_confidence:0,
signals:{
high_risk_clusters:[],
hub_entities:[],
shared_package_patterns:[],
method_similarity_patterns:[]
}
},


risk:{
score:0,
level:"UNKNOWN",
case_status:"",
engine:""
},


graph:{
entities:0,
relationships:0
},


evidence:{
score:0,
level:"",
total:0,
verified:0,
rejected:0,
pending:0,
custody_events:0,
confidence_level:"",
recommendation:""
},


findings:{
total:0,
critical:0,
high:0,
medium:0,
findings:[]
}

};


}



return {


case_id:data.case_id,



fraud:{

overall_risk:
data.fraud?.overall_risk ?? "UNKNOWN",


active_alerts:
data.fraud?.active_alerts ?? 0,


high_confidence:
data.fraud?.high_confidence ?? 0,


signals:{

high_risk_clusters:
data.fraud?.signals?.high_risk_clusters ?? [],


hub_entities:
data.fraud?.signals?.hub_entities ?? [],


shared_package_patterns:
data.fraud?.signals?.shared_package_patterns ?? [],


method_similarity_patterns:
data.fraud?.signals?.method_similarity_patterns ?? []

}

},




risk:{

score:
data.risk?.score ?? 0,


level:
data.risk?.level ?? "UNKNOWN",


case_status:
data.risk?.case_status ?? "",


engine:
data.risk?.engine ?? ""

},




graph:{

entities:
data.graph?.entities ?? 0,


relationships:
data.graph?.relationships ?? 0

},




evidence:{

score:
data.evidence?.score ?? 0,


level:
data.evidence?.level ?? "",


total:
data.evidence?.total ?? 0,


verified:
data.evidence?.verified ?? 0,


rejected:
data.evidence?.rejected ?? 0,


pending:
data.evidence?.pending ?? 0,


custody_events:
data.evidence?.custody_events ?? 0,


confidence_level:
data.evidence?.confidence_level ?? "",


recommendation:
data.evidence?.recommendation ?? "",


components:
data.evidence?.components

},




findings:{

total:
data.findings?.total ?? 0,


critical:
data.findings?.critical ?? 0,


high:
data.findings?.high ?? 0,


medium:
data.findings?.medium ?? 0,


findings:
data.findings?.findings ?? []

}



};


}
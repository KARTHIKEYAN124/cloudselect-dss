export const criteria = ['cost','security','scalability','performance','management'] as const
export type Criterion = typeof criteria[number]
export type Requirements = {workload:string;budget_eur:number;min_vcpu:number;min_ram_gib:number;storage_gb:number;hours:number;egress_gb:number;region:string;required_security:string[];weights:Record<Criterion,number>}
export const defaults:Requirements = {workload:'web_application',budget_eur:100,min_vcpu:2,min_ram_gib:8,storage_gb:100,hours:730,egress_gb:100,region:'europe',required_security:[],weights:{cost:30,security:25,scalability:20,performance:15,management:10}}
export type Alternative = {id:string;provider:string;service:string;instance_type:string;region:string;vcpu:number;ram_gib:number;source_url:string;pricing_url:string;accessed_date:string;data_status:string;security_capabilities:string[];evidence:Record<Criterion,string>;ratings:Record<Criterion,number>;contributions:Record<Criterion,number>;monthly_cost_eur:number;cost_breakdown:Record<string,number>;eligible:boolean;reasons:string[];rank:number|null;weighted_score:number|null;explanation?:string}
export type Evaluation = {status:string;results:Alternative[];requirements:Requirements;winners:string[];methodology:string}
export type Experiment = {criterion:Criterion;winners:string[];changed:boolean;weights:Record<Criterion,number>;results:{id:string;provider:string;score:number|null;rank:number|null}[]}
export type Scenario = {id:string;name:string;description:string;requirements:Partial<Requirements>}

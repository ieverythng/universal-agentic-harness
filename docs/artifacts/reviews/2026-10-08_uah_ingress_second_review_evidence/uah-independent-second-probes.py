import importlib.util, json, tempfile
from dataclasses import replace
from pathlib import Path
from ab_harness import EnvironmentIngress, EnvironmentTaskRegistry, LifecycleLedger, TaskIngressAuthority, TaskSpecCompiler
from ab_harness.lifecycle import TaskStartedFact

def fixture(name):
    spec=importlib.util.spec_from_file_location(name,Path.cwd()/'tests'/f'{name}.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
E=fixture('test_environment_ingress'); C=fixture('test_task_compiler')
results=[]
def probe(name, fn):
    try: results.append({'case':name,'result':fn()})
    except Exception as e: results.append({'case':name,'error':type(e).__name__,'message':str(e)})
def ingress(**changes):
    vals=dict(environment_ingress_id='ingress:independent:1',environment_run_id='environment-run:synthetic:001',binding_id='binding:synthetic.request:v1',ingress_type='user_request',payload_artifact_id='payload:independent:1',native_lineage=(('goal_id','goal:independent:1'),),observed_at='2026-09-13T09:00:00Z')
    vals.update(changes); return EnvironmentIngress(**vals)
def admission(changes):
    ledger=LifecycleLedger(); auth=TaskIngressAuthority(environment_profile_id='environment-profile:synthetic:v1',domain_contract_pack=E.DOMAIN_PACK,lifecycle_ledger=ledger)
    d=auth.admit(E._active_environment_run(),ingress(**changes))
    return {'action':d.action,'reason':d.reason_code,'events':len(ledger.events()),'task':d.task_id}
for name,changes in [
 ('valid',{}),('missing_lineage',{'native_lineage':()}),('null_lineage',{'native_lineage':None}),('empty_task',{'native_lineage':(('goal_id',''),)}),('unicode_task',{'native_lineage':(('goal_id','goal:αß🤖'),)}),('space_task',{'native_lineage':(('goal_id',' goal:1 '),)}),('unknown_binding',{'binding_id':'binding:unknown'}),('unknown_type',{'ingress_type':'unrecognized'}),('wrong_run',{'environment_run_id':'environment-run:wrong'}),('two_lineage_ab',{'native_lineage':(('goal_id','goal:1'),('request_id','request:1'))}),('two_lineage_ba',{'native_lineage':(('request_id','request:1'),('goal_id','goal:1'))}),('duplicate_lineage',{'native_lineage':(('goal_id','goal:1'),('goal_id','goal:2'))}),('leap_day',{'observed_at':'2024-02-29T23:59:59Z'}),('year_boundary',{'observed_at':'2027-01-01T00:00:00Z'}),('offset_date',{'observed_at':'2026-09-13T11:00:00+02:00'}),('invalid_date',{'observed_at':'2026-02-29T00:00:00Z'}),('no_timezone',{'observed_at':'2026-09-13T09:00:00'})]: probe(name,lambda changes=changes:admission(changes))
def sequence(order):
    ledger=LifecycleLedger(); auth=TaskIngressAuthority(environment_profile_id='environment-profile:synthetic:v1',domain_contract_pack=E.DOMAIN_PACK,lifecycle_ledger=ledger); out=[]
    for id in order:
        d=auth.admit(E._active_environment_run(),ingress(environment_ingress_id='ingress:'+id,native_lineage=(('goal_id','goal:'+id),)))
        out.append((d.action,d.reason_code,d.task_id))
    return {'out':out,'events':len(ledger.events())}
for order in [[],['a'],['a','b'],['b','a'],['a','a']]:probe('sequence_'+str(order),lambda order=order:sequence(order))
probe('valid_compile',lambda:TaskSpecCompiler().compile(**C._compiler_inputs()).compiled_task_id)
def raw_compile():
    inputs=C._compiler_inputs(); d=inputs['task_ingress_decision']; ledger=LifecycleLedger()
    ledger.record(TaskStartedFact(environment_run_id=d.environment_run_id,task_id=d.task_id,trace_id=d.trace_id,environment_ingress_id=d.environment_ingress_id,ingress_artifact_id=d.environment_ingress_artifact_id,decision_id=d.decision_id,domain_contract_pack_revision=d.domain_contract_pack_revision))
    inputs['task_registry']=EnvironmentTaskRegistry(ledger)
    return TaskSpecCompiler().compile(**inputs).compiled_task_id
probe('raw_start_fresh_compile',raw_compile)
def changed_decision(field,value):
    inputs=C._compiler_inputs(); inputs['task_ingress_decision']=replace(inputs['task_ingress_decision'],**{field:value})
    return TaskSpecCompiler().compile(**inputs).compiled_task_id
for field,value in [('environment_run_id','run:other'),('environment_ingress_id','ingress:other'),('environment_ingress_artifact_id','artifact:other'),('domain_contract_pack_revision','sha256:other'),('task_id','task:other'),('trace_id','trace:other')]:probe('compile_changed_'+field,lambda field=field,value=value:changed_decision(field,value))
def restart():
    with tempfile.TemporaryDirectory(prefix='uah-independent-second-') as tmp:
        path=Path(tmp)/'ledger.jsonl'; ledger=LifecycleLedger(path); auth=TaskIngressAuthority(environment_profile_id='environment-profile:synthetic:v1',domain_contract_pack=E.DOMAIN_PACK,lifecycle_ledger=ledger)
        d=auth.admit(E._active_environment_run(),ingress()); restarted=LifecycleLedger(path)
        lineage=EnvironmentTaskRegistry(restarted).require_start(environment_run_id=d.environment_run_id,environment_ingress_id=d.environment_ingress_id,ingress_artifact_id=d.environment_ingress_artifact_id,decision_id=d.decision_id,domain_contract_pack_revision=d.domain_contract_pack_revision,task_id=d.task_id,trace_id=d.trace_id)
        return {'events':len(restarted.events()),'task':lineage.task_id}
probe('restart_require_start',restart)
print(json.dumps(results,indent=2))

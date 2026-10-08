import importlib.util,json,tempfile
from dataclasses import replace
from pathlib import Path
from ab_harness import EnvironmentIngress,LifecycleLedger,TaskIngressAuthority
spec=importlib.util.spec_from_file_location('eg',Path.cwd()/'tests/test_environment_ingress.py'); eg=importlib.util.module_from_spec(spec);spec.loader.exec_module(eg)
results=[]
def probe(name,fn):
 try: results.append({'case':name,'result':fn()})
 except Exception as e: results.append({'case':name,'error':type(e).__name__,'message':str(e)})
class CaptureLedger(LifecycleLedger):
 def record(self,value,**kw):
  self.last_command=value
  return super().record(value,**kw)
def admitted(ledger):
 run=eg._active_environment_run()
 item=EnvironmentIngress('ingress:second:boundaries',run.environment_run_id,'binding:synthetic.request:v1','user_request','artifact:second:boundaries',(('goal_id','task:second:boundaries'),),'2026-10-08T12:00:00Z')
 auth=TaskIngressAuthority(environment_profile_id=run.attestation.environment_profile_id,domain_contract_pack=eg.DOMAIN_PACK,lifecycle_ledger=ledger)
 return auth,run,item,auth.admit(run,item)
source=CaptureLedger(); authority,run,item,decision=admitted(source)
probe('captured_command_wrong_ledger',lambda:len(LifecycleLedger().record(source.last_command).events))
probe('captured_command_repeated',lambda:len(source.record(source.last_command).events))
for kind,value in [('event',source.events()[0]),('mapping',source.events()[0].to_dict()),('iterable',iter(source.events())),('replay',source.replay(decision.trace_id))]:
 probe('export_transfer_'+kind,lambda value=value:len(LifecycleLedger().record(value).events))
if hasattr(source.last_command,'capability'):
 command=source.last_command
 for name,changes in [('bad_capability',{'capability':object()}),('bad_decision',{'decision':replace(decision,reason_code='forged')}),('bad_ingress',{'ingress':replace(item,payload_artifact_id='artifact:other')}),('bad_run',{'environment_run':eg._active_environment_run('environment-run:other')})]:
  probe(name,lambda changes=changes:len(source.record(replace(command,**changes)).events))
 with tempfile.TemporaryDirectory(prefix='uah-second-affinity-') as tmp:
  path=Path(tmp)/'ledger.jsonl'; backed=CaptureLedger(path);admitted(backed)
  probe('same_path_other_instance',lambda:len(LifecycleLedger(path).record(backed.last_command).events))
print(json.dumps(results,indent=2))

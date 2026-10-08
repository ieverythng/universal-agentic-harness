import json, multiprocessing, tempfile
from pathlib import Path
from ab_harness import EnvironmentIngress,LifecycleLedger,TaskIngressAuthority
import importlib.util
spec=importlib.util.spec_from_file_location('eg',Path.cwd()/'tests/test_environment_ingress.py');eg=importlib.util.module_from_spec(spec);spec.loader.exec_module(eg)
def worker(path,barrier,queue,index,case):
 run=eg._active_environment_run()
 ledger=LifecycleLedger(path);auth=TaskIngressAuthority(environment_profile_id=run.attestation.environment_profile_id,domain_contract_pack=eg.DOMAIN_PACK,lifecycle_ledger=ledger)
 ingress_id='shared' if case=='same_ingress' else str(index)
 task_id='shared' if case in ('same_ingress','same_task') else str(index)
 item=EnvironmentIngress('ingress:proc:'+ingress_id,run.environment_run_id,'binding:synthetic.request:v1','user_request','artifact:proc:'+ingress_id,(('goal_id','task:proc:'+task_id),),'2026-10-08T12:00:00Z')
 barrier.wait()
 try:
  d=auth.admit(run,item);queue.put((d.action,d.reason_code))
 except Exception as e:queue.put((type(e).__name__,str(e)))
ctx=multiprocessing.get_context('fork');output=[]
for case in ['same_ingress','same_task','different_tasks']:
 with tempfile.TemporaryDirectory(prefix='uah-second-process-') as tmp:
  path=str(Path(tmp)/'ledger.jsonl');barrier=ctx.Barrier(2);queue=ctx.Queue()
  workers=[ctx.Process(target=worker,args=(path,barrier,queue,i,case)) for i in (0,1)]
  for p in workers:p.start()
  outcomes=[queue.get(timeout=15) for _ in workers]
  for p in workers:p.join(15)
  events=LifecycleLedger(path).events()
  output.append({'case':case,'outcomes':sorted(outcomes),'sequence':[e.sequence for e in events],'child_exit':[p.exitcode for p in workers]})
print(json.dumps(output,indent=2))

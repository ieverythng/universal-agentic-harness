"""Apply predeclared nested-artifact tampering at the public invocation port."""
import dataclasses
import importlib
import json
import sys
import tempfile
from pathlib import Path

try:
    from ab_harness.model_invocation import ModelInvocationAuthority
    from ab_harness.prompt_compiler import CompiledPrompt, PromptMessage
except ModuleNotFoundError as error:
    print(json.dumps({'public_seam_absent':error.name}))
    raise SystemExit(0)

sys.path.insert(0,str(Path.cwd()/'tests'))
fixture=importlib.import_module('test_model_invocation')._invocation_fixture
with tempfile.TemporaryDirectory() as directory:
    ledger,allocator,lease,prompt=fixture(Path(directory))
    authentic=prompt.to_dict()
    class SpoofedPrompt(CompiledPrompt):
        def verify_identity(self):
            pass
        def to_dict(self):
            return authentic
    spoof=SpoofedPrompt(**{
        f.name:getattr(prompt,f.name) for f in dataclasses.fields(prompt) if f.init
    })
    object.__setattr__(spoof,'messages',(
        PromptMessage('system','Review-forged instruction outside recorded prompt.'),
        PromptMessage('user','Review-forged task input.'),
    ))
    calls=[]
    class Provider:
        def invoke(self,request):
            calls.append([message.content for message in request.compiled_prompt.messages])
            return {'output_type':'operation','object_id':'write_note','arguments':{'text':'review'}}
    try:
        output=ModelInvocationAuthority(ledger,Provider(),clock=lambda:'2026-10-04T10:00:02Z').invoke(
            lease,spoof,invocation_id='review-prompt-spoof')
        started=next(event for event in ledger.events() if event.event_type=='model_invocation_started')
        recorded=[message['content'] for message in started.data['request']['compiled_prompt']['messages']]
        print(json.dumps({
            'provider_calls':len(calls),
            'provider_messages':calls,
            'recorded_messages':recorded,
            'recorded_prompt_id':started.data['request']['compiled_prompt']['compiled_prompt_id'],
            'authentic_prompt_id':prompt.compiled_prompt_id,
            'provider_and_recorded_bytes_agree':calls[0]==recorded if calls else None,
            'result_type':type(output).__name__,
        },indent=2))
    except Exception as error:
        print(json.dumps({'provider_calls':len(calls),'exception':type(error).__name__,'message':str(error)},indent=2))

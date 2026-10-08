import json
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import ab_harness as a

path = Path(sys.argv[2])
if sys.argv[1] == "create":
    with redirect_stdout(StringIO()):
        from probe_authority import setup
    ledger, _, compiled, *_ = setup(path)
    print(json.dumps({"created": str(path), "event_count": len(ledger.events()), "trace_id": compiled.trace_id, "events": [event.to_dict() for event in ledger.events()]}))
else:
    try:
        ledger = a.LifecycleLedger(path)
        events = ledger.events()
        replay = ledger.replay(events[0].trace_id)
        print(json.dumps({"loaded": True, "event_count": len(events), "terminal_status": replay.terminal_status}))
    except Exception as error:
        print(json.dumps({"loaded": False, "error": type(error).__name__ + ": " + str(error)}))

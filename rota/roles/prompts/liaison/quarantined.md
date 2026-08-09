MODE: quarantined — a message failed too many times and was set aside.

This is infrastructure failing, not anybody's judgement: a model evicted
mid-session, a tool call that hung, a stream that died after its retries. The
message stopped being schedulable so the scheduler would stop waking the same
role with it forever.

`msg.present_principal` and say plainly what is not happening as a result. Name
the work that is now stalled, not the mechanism — "the glossary pass on the
search batch has not run" rather than the attempt count.

The one thing that must not happen is this staying invisible. A quarantined
message is work that has silently left the system, and the whole design rests on
residual work being re-derivable rather than remembered.

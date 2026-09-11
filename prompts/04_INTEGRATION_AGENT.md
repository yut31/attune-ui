# Integration Agent Prompt

Follow `prompts/00_MASTER_AGENT_PROMPT.md`.

## Role

You connect already-tested pieces together.

You should not redesign either side of an interface.

## Integration principle

Prefer adapters.

Example:

```text
real pipeline output
       |
       v
small adapter
       |
       v
stable UI payload
       |
       v
frontend
```

Do not make frontend components understand raw EEG/model internals.

## Required tests

At minimum:

- valid end-to-end message,
- malformed message,
- backend unavailable/disconnected,
- startup with no EEG source,
- deterministic mock path still works.

If integration requires changing the stable application contract, stop and document the proposed contract change before implementing it.

*This activity has been created as part of the 42 curriculum by mde-nas.*

# call me maybe

## Description

A function-calling tool that translates natural language prompts into structured
function calls (name + typed arguments) using a small local LLM (Qwen3-0.6B).
Structural validity (100% parseable JSON matching the function schema) is
guaranteed by **constrained decoding**: at each generation step, invalid tokens
are masked out before the model picks the next one, instead of hoping the model
spontaneously produces correct JSON from a prompt.

## Instructions

Requires `uv`. `llm_sdk/` must sit next to `src/` (already the case in this repo).

```bash
make install   # uv sync
make run       # uv run python -m src
```

Custom paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Other targets: `make lint`, `make lint-strict`, `make debug`, `make clean`.

> On this machine, `/home` is a small partition — the `Makefile` redirects the
> `uv` virtual environment to `/goinfre/$(USER)/call_me_maybe/.venv` via
> `UV_PROJECT_ENVIRONMENT` to avoid filling it up with `torch`/`transformers`.

## Algorithm: constrained decoding

The model never generates JSON punctuation (`{`, `"name":`, `,`, `}`...) — that
scaffolding is written directly in Python. The LLM is only asked to fill in the
semantically meaningful slots: the function name and each parameter's value.
For each slot, the token-selection rule differs:

- **Closed choices** (function name, booleans): a trie/prefix check
  (`valid_token_id`). A token is valid if appending it still forms a prefix of
  at least one candidate string; the model picks the best-scoring valid token,
  the candidate list narrows each step, and generation stops once exactly one
  full candidate remains.
- **Numbers**: a small character-class state machine (`is_valid_number_token`)
  allows digits, one optional leading `-`, one optional `.`. The model's own
  unconstrained top choice is accepted whenever it's already legal; masking
  only kicks in to force a digit when the natural choice would break the
  grammar. Generation stops once a complete number exists and the model's
  natural next pick isn't a digit.
- **Strings**: no character masking is needed — `json.dump` escapes special
  characters automatically at write time. The prompt ends with an opening
  `"`, which nudges the model into "continuing a quoted string"; generation
  stops as soon as it picks a token containing `"`.

Token IDs are mapped back to real text via `vocab.py`, which reimplements the
GPT-2/Qwen byte-level BPE `bytes_to_unicode` table (`vocab.json` alone only
gives obfuscated byte-level strings, e.g. `Ġ` for a leading space).

## Design decisions

- One module per responsibility: `models.py` (pydantic schemas), `loader.py`
  (I/O + validation), `vocab.py` (tokenizer decoding), `chose_function.py`
  (function selection), `parameters.py` (parameter value generation),
  `__main__.py` (CLI + orchestration).
- A dedicated prompt is built per decision (function selection lists all
  functions with descriptions; each parameter prompt names the function, all
  its parameters, and the one being asked for) — accuracy comes from giving
  the model enough framing, constrained decoding only guarantees structure.

## Performance analysis

On the 11 provided prompts: 11/11 correct function selection, 9/11 fully
correct parameters, 100% valid/schema-compliant JSON, ~150s total on CPU.
`make lint` (flake8 + mypy with
`--disallow-untyped-defs --check-untyped-defs`) passes cleanly.

## Challenges faced

- **Disk space**: the small `/home` partition filled up during the first
  `uv sync` (torch/transformers); fixed by redirecting the venv and caches to
  `/goinfre`.
- **`accelerate` crash**: `Small_LLM_Model()` raised a `device_map` error on
  machines where CUDA is visible; fixed by forcing `device="cpu"`.
- **Uninformed function choice**: without describing the available functions
  in the prompt, the model picked the same function regardless of the
  question — fixed by including function names/descriptions and an explicit
  instruction before generating.

## Testing strategy

The full pipeline was validated against the 11 provided prompts, and
`make lint` was run after every change.

## Example usage

```bash
$ make run
Wrote 11 results to data/output/function_calling_results.json
```

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": { "a": 2, "b": 3 }
}
```

## Resources

- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [GPT-2 `bytes_to_unicode` encoding](https://github.com/openai/gpt-2/blob/master/src/encoder.py) — reference for the byte-level BPE decoding in `vocab.py`
- [JSON Schema](https://json-schema.org/) — for the `type` field semantics in `functions_definition.json`
- [Pydantic docs](https://docs.pydantic.dev/)

**AI usage**: Claude was used throughout as a tutor/reviewer, not a code
generator — all code was written by hand. It was used to: explain concepts
(tokenization, byte-level BPE, constrained decoding, argparse, Pylance/mypy
typing quirks) before writing code; point out concrete bugs and write this
README

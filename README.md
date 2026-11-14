# Constrained Decoding

**Stack:** Python · Hugging Face Transformers / PyTorch · Qwen3-0.6B · Pydantic · uv

Function calling with a small local LLM, made reliable through **constrained decoding**: instead of hoping the model outputs valid JSON, every generated token is filtered so the output can only be a valid function name or a well-typed argument.

> 🚧 Work in progress: the decoding core is implemented, the end-to-end pipeline (argument extraction and result writing) is being wired up.

## How it works

1. **Vocabulary decoding** (`src/vocab.py`): loads the tokenizer's `vocab.json` and reverses the byte-level BPE mapping, so each token id maps to the exact text it produces.
2. **Token masking** (`src/chose_function.py`): at each step, only tokens that keep the generated text a prefix of at least one valid candidate are allowed. The model picks the highest-logit token among those.
3. **Early stop**: generation ends as soon as the text matches exactly one candidate, so the model can never produce an unknown function name.
4. **Typed values**: the same mechanism constrains booleans (`true` / `false`), with numbers and strings next.

## Usage

```bash
make install   # uv sync + dev tools
make run       # python -m src
make lint      # flake8 + mypy
```

Options:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

## Input format

`functions_definition.json` describes the callable functions:

```json
{
  "name": "fn_add_numbers",
  "description": "Add two numbers together and return their sum.",
  "parameters": { "a": { "type": "number" }, "b": { "type": "number" } },
  "returns": { "type": "number" }
}
```

`function_calling_tests.json` lists natural-language prompts (`"What is the sum of 2 and 3?"`). The expected output for each prompt is the chosen function and its typed arguments:

```json
{ "prompt": "What is the sum of 2 and 3?", "name": "fn_add_numbers", "parameters": { "a": 2, "b": 3 } }
```

## Project structure

| Path | Role |
|---|---|
| `src/__main__.py` | CLI entry point |
| `src/vocab.py` | Token id → text mapping (byte-level BPE decoding) |
| `src/chose_function.py` | Constrained generation over a set of candidates |
| `src/loader.py`, `src/models.py` | JSON loading and Pydantic models |
| `llm_sdk/` | Thin wrapper around the Hugging Face model (encode, logits, decode) |

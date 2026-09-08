import json
from src.models import FunctionDefinition, PromptItem
from typing import Any
from pydantic import TypeAdapter, ValidationError
from pathlib import Path


def load_json(path: Path) -> Any:
    """
    Export the json to read it and parse it
    """
    try:
        with path.open('r') as file:
            return json.load(file)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found : {path}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Inavlid json in {path}: {e}") from e


def load_function_definition(path: Path) -> list[FunctionDefinition]:
    """
    Load a list of function definition using path
    """
    raw = load_json(path)
    try:
        return TypeAdapter(list[FunctionDefinition]).validate_python(raw)
    except ValidationError as e:
        raise ValueError(f"Schema error in {path}: {e}") from e


def load_prompt(path: Path) -> list[PromptItem]:
    """
    Load a list of prompt item using path
    """
    raw = load_json(path)
    try:
        return TypeAdapter(list[PromptItem]).validate_python(raw)
    except ValidationError as e:
        raise ValueError(f"Schema error in {path}: {e}") from e

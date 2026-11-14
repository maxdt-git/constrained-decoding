from pydantic import BaseModel
from typing import Any


class ParameterItem(BaseModel):
    """
    Stock item instead of calling everytime after
    """
    type: str


class FunctionDefinition(BaseModel):
    """
    Stock the function_definition.json values
    """
    name: str
    description: str
    parameters: dict[str, ParameterItem]
    returns: ParameterItem


class PromptItem(BaseModel):
    """
    Stock the prompt to call it easily in FunctionResult
    """
    prompt: str


class FunctionResult(BaseModel):
    """
    Represent a return value of the output file
    """
    prompt: str
    name: str
    parameters: dict[str, Any]

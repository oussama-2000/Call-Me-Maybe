"""pydantic models"""
from pydantic import BaseModel, Field
from typing import Dict


class Prompt(BaseModel):
    prompt: str = Field(min_length=6)


class Function_definition(BaseModel):
    name: str = Field(min_length=8)
    description: str = Field(min_length=6)
    parameters: Dict[str, Dict[str, str]] = Field(min_length=1)
    returns: Dict[str, str]

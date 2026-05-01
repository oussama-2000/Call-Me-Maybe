"""pydantic models"""
from pydantic import BaseModel, Field, model_validator
from typing import Dict


class Prompt(BaseModel):
    prompt: str = Field(min_length=6)

    @model_validator(mode='after')
    def custom(self):
        self.prompt = self.prompt.strip()
        if len(self.prompt) < 6:
            raise ValueError("prompt lenght must be 6 at least")
        return self


class Function_definition(BaseModel):
    name: str = Field(min_length=8)
    description: str = Field(min_length=6)
    parameters: Dict[str, Dict[str, str]] = Field(min_length=1)
    returns: Dict[str, str]

    @model_validator(mode='after')
    def custom(self):
        self.name = self.name.strip()
        self.description = self.description.strip()

        if not self.name:
            raise ValueError("empty function name")
        if not self.description:
            raise ValueError("empty desctionption")

        for i in self.parameters.values():
            if len(tuple(i.items())) != 1 or \
                    tuple(i.items())[0][0] != "type":
                raise ValueError("the only acceptable parametter key is 'type'")

        if len(tuple(self.returns.items())) != 1 or \
                tuple(self.returns.items())[0][0] != "type":
            raise ValueError("the only acceptable returns key is 'type'")
        return self

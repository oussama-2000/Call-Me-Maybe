try:
    from pydantic import BaseModel, Field, model_validator
    from typing import Dict
except ImportError as e:
    print(f"Import Error: {e}")
    exit()


class Prompt(BaseModel):
    """
        base model to validate prompts
    """
    prompt: str

    @model_validator(mode='after')
    def custom(self) -> "Prompt":
        """
            custom validation for more prompt validation
        """
        self.prompt = self.prompt.strip()
        if not self.prompt:
            raise ValueError("prompt must not be empty")

        return self


class Function_definition(BaseModel):
    """
        base model to validate functions definition
    """
    name: str
    description: str = Field(min_length=6)
    parameters: Dict[str, Dict] = Field(min_length=1)
    returns: Dict[str, str]

    @model_validator(mode='after')
    def custom(self) -> "Function_definition":
        """
            custom validation for more functions definition validation
        """
        self.name = self.name.strip()
        self.description = self.description.strip()

        allowed_type = ["number", "string", "integer", "boolean"]

        if not self.name:
            raise ValueError("empty function name")

        if not self.description:
            raise ValueError("empty desctionption")

        for k in self.parameters.keys():
            if not k.strip():
                raise ValueError("invalid parametter name")

        for i in self.parameters.values():
            if len(tuple(i.items())) != 1 or \
                    tuple(i.items())[0][0] != "type":
                raise ValueError("the only acceptable"
                                 " parametter key is 'type'")

            if tuple(i.items())[0][1] not in allowed_type:
                raise ValueError("unsupported parameter type:"
                                 f" {tuple(i.items())[0][1]}")

        if len(tuple(self.returns.items())) != 1 or \
                tuple(self.returns.items())[0][0] != "type":
            raise ValueError("the only acceptable returns key is 'type'")

        if tuple(self.returns.items())[0][1] not in allowed_type:
            raise ValueError("unsupported return type:"
                             f" {tuple(self.returns.items())[0][1]}")
        return self

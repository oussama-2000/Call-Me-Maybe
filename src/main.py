from .parser import Parser
from pydantic import ValidationError
from .gen import build_prompt, generate


if __name__ == "__main__":
    try:
        parser = Parser()

        prompts, functions = parser.parsing()

        data = {
            "prompts": prompts,
            "functions": functions
        }

        for prompt in prompts:
            p = build_prompt(prompt.prompt)
            print(generate(p))

    except ValidationError as e:
        print(f"Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

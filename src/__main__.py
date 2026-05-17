from .parser import Parser
from pydantic import ValidationError
from .gen import build_prompt, generate, build_functions
from datetime import datetime


if __name__ == "__main__":
    try:
        parser = Parser()

        prompts, functions = parser.parsing()

        functions_definitions = build_functions(functions)
        # prompt = "what is the sum of 2 and 40"
        # p = build_prompt(prompt, functions_definitions)
        # generate(p, prompt, functions_definitions)
        start = datetime.now()
        for prompt in prompts:
            p = build_prompt(prompt.prompt, functions_definitions)
            print(generate(p, prompt.prompt, functions_definitions))
        end = datetime.now()

        print(f"time: {end - start}")
    except ValidationError as e:
        print(f"Parsing Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

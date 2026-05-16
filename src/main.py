from .parser import Parser
from pydantic import ValidationError
from .gen import build_prompt, generate, build_functions
from datetime import datetime



if __name__ == "__main__":
    try:
        parser = Parser()

        prompts, functions = parser.parsing()

        data = {
            "prompts": prompts,
            "functions": functions
        }
        functions_definitions = build_functions(data['functions'])
        prompt = "Replace all vowels in 'Programming is fun' with asterisks"
        p = build_prompt(prompt, functions_definitions)
        generate(p, prompt, functions_definitions)
        # start = datetime.now()
        # for prompt in prompts:
        #     p = build_prompt(prompt.prompt)
        #     print(generate(p, prompt.prompt))
        
        # end = datetime.now()
        # print(f"time: {end - start}")
    except ValidationError as e:
        print(f"Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

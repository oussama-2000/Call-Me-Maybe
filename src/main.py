from parser import Parser
from pydantic import ValidationError


if __name__ == "__main__":
    try:
        parser = Parser()

        loading_prompts, loading_functions = parser.parsing()

        print(parser.load_prompts(loading_prompts))
        print("----")
        print(parser.load_functions_definition(loading_functions))

    except ValidationError as e:
        print(f"Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

from parser import Parser
from pydantic import ValidationError


if __name__ == "__main__":
    try:
        parser = Parser()

        prompts, functions = parser.parsing()

        data = {
            "prompts": prompts,
            "functions": functions
        }
        print(data)

    except ValidationError as e:
        print(f"Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

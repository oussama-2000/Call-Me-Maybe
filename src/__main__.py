from .parser import Parser
# from .generator import Generator
from pydantic import ValidationError
from datetime import datetime
from argparse import ArgumentParser
import os
import json

if __name__ == "__main__":
    try:
        args_parser = ArgumentParser()

        args_parser.add_argument(
            "--functions_definition",
            default="./data/input/functions_definition.json"
            )
        args_parser.add_argument(
            "--input",
            default="./data/input/function_calling_tests.json"
            )
        args_parser.add_argument(
            "--output",
            default="./data/output/function_calls.json"
            )

        args = args_parser.parse_args()

        parser = Parser()
        prompts, functions = parser.parsing(
            args.functions_definition,
            args.input
            )
        print(functions)
        # os.makedirs(os.path.dirname(args.output), exist_ok=True)

        # generator = Generator(functions)
        # output = []
        # start = datetime.now()

        # for prompt in prompts:
        #     p = generator.build_prompt(prompt.prompt)
        #     result = generator.generate(p, prompt.prompt)
        #     print(result)
        #     output.append(json.loads(result))
        # end = datetime.now()

        # print(f"time: {end.minute - start.minute} minutes")

        # with open(args.output, "w") as f:
        #     json.dump(output, f, indent=4)

    except ValidationError as e:
        print(f"Parsing Error: {e.errors()[0]['msg']}")
    except Exception as e:
        print(f"Error: {e}")

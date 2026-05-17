import json
from json import JSONDecodeError
from .models import Prompt, Function_definition
from typing import List


class Parser():

    def load_json_file(self, path: str) -> List:
        try:

            with open(path, "r") as file:
                # content = file.read().strip()
                # if not content:
                #     raise ValueError("Empty file")
                return json.load(file)

        except json.JSONDecodeError as e:
            file_name = path.split("/")[-1]
            raise ValueError(f"invalid json file '{file_name}'"
                             f": {e} ")

    def parsing_functions_definition(self,
                                  json: str) -> List[Function_definition]:

        return [Function_definition(**i) for i in json]

    def parsing_prompts(self, prompts: str) -> List[Prompt]:

        return [Prompt(**i) for i in prompts]

    def parsing(self):

        loading_prompts = \
            self.load_json_file("./data/input/function_calling_tests.json")
        loading_functions = \
            self.load_json_file("./data/input/functions_definition.json")

        if not isinstance(loading_prompts, list):
            raise ValueError("invalid prompts !")
        if not isinstance(loading_functions, list):
            raise ValueError("invalid functions !")
        if not loading_prompts:
            raise ValueError("no prompts provided !")
        if not loading_functions:
            raise ValueError("no definition functions provided !")

        functions = self.parsing_functions_definition(loading_functions)
        prompts = self.parsing_prompts(loading_prompts)

        return (prompts, functions)

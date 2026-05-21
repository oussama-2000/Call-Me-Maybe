try:
    import json
    from json import JSONDecodeError
    from .models import Prompt, Function_definition
    from typing import List, Tuple, Any
except ImportError as e:
    print(f"Import Error: {e}")
    exit()


class Parser():
    """
        this class contains the parsing functionalities
    """
    def parsing(self, fns: str, input: str) -> Tuple:
        """
            main input parsing function
        """
        loading_prompts = self.load_json_file(input)
        loading_functions = self.load_json_file(fns)

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

    def load_json_file(self, path: str) -> Any | None:
        """
            helper json file load funciton
        """
        try:

            with open(path, "r") as file:
                # file_name = path.split("/")[-1]
                # content = file.read().strip()
                # if not content:
                #     raise ValueError("Empty file")
                return json.load(file)

        except JSONDecodeError as e:
            file_name = path.split("/")[-1]
            raise ValueError(f"invalid json file '{file_name}'"
                             f": {e} ")

    def parsing_functions_definition(self,
                                     json: List) -> List[Function_definition]:
        """
            this function calls pydantic parsing models
            to pars function definition file content
        """
        return [Function_definition(**i) for i in json]

    def parsing_prompts(self, prompts: List) -> List[Prompt]:
        """
            this function calls pydantic parsing models
            to pars prompt file content
        """
        return [Prompt(**i) for i in prompts]

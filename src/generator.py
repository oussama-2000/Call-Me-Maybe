import json
import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model
from typing import List, Dict, Tuple


class Generator:
    """
        this class responsable about generation
        and constrained decoding functionalities
    """
    def __init__(self, functions: List) -> None:
        self.llm = Small_LLM_Model()
        self.functions = self.build_functions(functions)

    def build_functions(self, input: List) -> Dict:
        for fn in input:
            for par in fn.parameters:
                if fn.parameters[par]["type"] == "number":
                    fn.parameters[par]["type"] = "float"

        functions = {
                        fn.name: {
                                par: fn.parameters[par]["type"]
                                for par in fn.parameters
                            }
                        for fn in input
                    }
        functions['fn_unknown'] = None

        return functions

    def build_prompt(self, user_prompt: str) -> str:
        """
            this function generates the main prompt should passed
            to the llm to understande the context (prompting)
        """

        return f"""
        You convert user requests into function calls.

        Format:
        {{
        "prompt": user prompt,
        "name": string,
        "parameters": object
        }}

        EXAMPLE:
        User prompt: "What is the square root of 16?"
        JSON:
        {{
            "prompt": "What is the square root of 16?",
            "name": "fn_get_square_root",
            "parameters": {{"a": 16.0}}
        }}

        FUNCTIONS:
        {self.functions}

        Task:
        User prompt: {user_prompt}
        JSON:
        """

    def is_valid_prefix(self, text: str) -> bool:
        """
            this function checks if the result still valid
            when adding next pridected token
        """

        if text.count("}") > text.count("{"):
            return False

        if '"name":' in text:

            name_parts = text.split('"name"')[1]
            fn_part = name_parts.split(":")[1]
            if fn_part.count('"') < 2:
                fn_part = fn_part.replace('"', "")
                fn_part = fn_part.replace(',', "")
                fn_part = fn_part.strip()
                fn_validation = any(
                    fn.startswith(fn_part)
                    for fn in self.functions
                )

                return fn_validation

        if '"parameters": {"' in text:
            par_parts = text.split('"parameters": {"')[1]
            par_parts = par_parts.replace('"', "")
            par_parts = par_parts.replace('}', "")
            values = par_parts.split(",")
            for value in values:
                if ":" in value:
                    key = value.split(":")[0].strip()
                    par_validation = any(
                        key in v for v in self.functions.values()
                    )
                    return par_validation

        return True

    def is_json_complete(self, text: str) -> bool:
        """
            this function checks if the json completed or not
            to stop tokens generation
        """

        if text.count("{") == text.count("}"):
            return True
        return False

    def generate(self, prompt: str, user_prompt: str) -> str:
        """
            this function is the generation engine
        """

        input_ids = list(self.llm.encode(prompt)[0])
        result = []
        prefix = json.dumps({
            "prompt": user_prompt,
            "name": ""
        }, indent=4)[:-3]

        prefix_ids = list(self.llm.encode(prefix)[0])
        input_ids += prefix_ids
        result = prefix_ids.copy()
        fn_search_done = False
        fn_name = None

        while True:
            if not fn_search_done:
                exists, name = self.search_for_fn(
                    self.llm.decode(result).split()[-1])

                if name == "fn_unknown":
                    raise ValueError("Invalid prompt")

                if exists:
                    p_key_ids = list(self.llm.encode('", "parameters": {"')[0])
                    input_ids += p_key_ids
                    result.extend(p_key_ids)
                    input_ids += list(self.llm.encode(
                        f'{list(self.functions[name])[0]}": ')[0])
                    result += list(self.llm.encode(
                        f'{list(self.functions[name])[0]}": ')[0])
                    fn_search_done = True
                    fn_name = name

            if fn_search_done:
                if self.in_pars(self.llm.decode(result).split()[-1], fn_name):
                    token_ids = list(self.llm.encode('": ')[0])
                    input_ids += token_ids
                    result.extend(token_ids)

            logits = self.llm.get_logits_from_input_ids(input_ids)

            logits = np.array(logits)

            top_logits = np.argsort(logits)[-3:]

            selected_token = None

            for logit in reversed(top_logits):

                test_ids = result + [logit]

                text = self.llm.decode(test_ids)
                # print(f"{text}")

                if self.is_valid_prefix(text):
                    selected_token = logit
                    break

            if selected_token is None:
                selected_token = np.argmax(logits)

            input_ids.append(selected_token)
            result.append(selected_token)

            if self.llm.decode(selected_token).strip().endswith("\\"):
                escape_ids = list(self.llm.encode("\\")[0])
                input_ids += escape_ids
                result.extend(escape_ids)

            if self.is_json_complete(self.llm.decode(result)):
                break

        return self.llm.decode(result)

    def search_for_fn(self, last_item: str) -> Tuple:
        """
            this function checks if function name is exitst into result
            for adding '"prompt": ' key to result
            without letting llm pridect it
        """
        fn = last_item.replace('"', "")
        if fn.strip() in self.functions:
            return True, fn
        return False, None

    def in_pars(self, last_item: str, fn_name: str) -> bool:
        """
            this function checks if we currently in a function parametter
        """
        par = last_item.replace('"', "")
        if par.strip() in self.functions[fn_name]:
            return True
        return False

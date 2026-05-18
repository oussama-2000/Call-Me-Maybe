import json
import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()


def build_functions(input):
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


def build_prompt(user_prompt, functions):
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
    {functions}

    Task:
    User prompt: {user_prompt}
    JSON:
    """


def is_valid_prefix(text, functions) -> bool:

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
                for fn in functions
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
                    key in v for v in functions.values()
                )
                return par_validation

    return True


def is_json_complete(text: str) -> bool:
    if text.count("{") == text.count("}"):
        return True
    return False


def generate(prompt, user_prompt, functions):

    input_ids = llm.encode(prompt)[0].tolist()
    result = []
    prefix = json.dumps({
        "prompt": user_prompt,
        "name": ""
    })[:-2]

    prefix_ids = llm.encode(prefix)[0].tolist()
    input_ids += prefix_ids
    result = prefix_ids.copy()
    fn_search_done = False
    fn_name = None

    while True:
        if not fn_search_done:
            exists, name = search_for_fn(
                llm.decode(result).split()[-1], functions)

            if name == "fn_unknown":
                raise ValueError("Invalid prompt")

            if exists:
                p_key_ids = llm.encode('", "parameters": {"')[0].tolist()
                input_ids += p_key_ids
                result.extend(p_key_ids)
                input_ids += llm.encode(f'{list(functions[name])[0]}": ')[0].tolist()
                result += llm.encode(f'{list(functions[name])[0]}": ')[0].tolist()
                fn_search_done = True
                fn_name = name

        if fn_search_done:
            if in_pars(llm.decode(result).split()[-1], fn_name, functions):
                token_ids = llm.encode('": ')[0].tolist()
                input_ids += token_ids
                result.extend(token_ids)

        logits = llm.get_logits_from_input_ids(input_ids)

        logits = np.array(logits)

        top_logits = np.argsort(logits)[-3:]

        selected_token = None

        for logit in reversed(top_logits):

            test_ids = result + [logit]

            text = llm.decode(test_ids)
            print(f"{text}")

            if is_valid_prefix(text, functions):
                selected_token = logit
                break

        if selected_token is None:
            selected_token = np.argmax(logits)

        input_ids.append(selected_token)
        result.append(selected_token)

        if is_json_complete(llm.decode(result)):
            break

    return llm.decode(result)


def search_for_fn(last_item, functions):
    """
        this function checks if function name is exitst in result
        for adding '"prompt": ' key to result without letting llm pridect it
    """
    fn = last_item.replace('"', "")
    if fn.strip() in functions:
        return True, fn
    return False, None


def in_pars(last_item, fn_name, functions):
    """
        this function checks if we currently in a function parametters
    """
    par = last_item.replace('"', "")
    if par.strip() in functions[fn_name]:
        return True
    return False

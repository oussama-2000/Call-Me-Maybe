import json
import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()


def build_functions(input):
    functions = {fn.name: list(fn.parameters.keys())
                    for fn in input
                }
    functions['fn_unknown'] = None
    return functions

def build_prompt(user_prompt, functions):
    return f"""
    You convert user requests into function calls.
    
    RETURN ONLY VALID MINIFIED JSON.
    
    Format:
    {{
      "prompt": user prompt
      "name": string enum{list(functions.keys())},
      "parameters": object
    }}
    
    FUNCTIONS:
    {functions}
    
    YOU MUST RESPECT PARAMETERS TYPE.
    
    Task:
    User prompt: {user_prompt}
    JSON:
    """


def is_valid_prefix(text: str, functions) -> bool:
    
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
    try:

        text = text.replace("\\d", "\\\\d")
        text = text.replace("\\s", "\\\\s")
        obj = json.loads(text)

        if not isinstance(obj, dict):
            return False
    
        return True

    except Exception:
        return False



def generate(prompt, user_prompt, functions):

    input_ids = list(llm.encode(prompt)[0])
    result = []
    prefix = json.dumps({
        "prompt": user_prompt,
        "name": ""
    })[:-3]
    prefix_ids = list(llm.encode(prefix)[0])
    input_ids += prefix_ids
    result = prefix_ids.copy()

    for _ in range(100):

        logits = llm.get_logits_from_input_ids(input_ids)

        logits = np.array(logits)

        top_logits = np.argsort(logits)[-5:]

        selected_token = None

        for logit in reversed(top_logits):

            test_ids = result + [int(logit)]

            text = llm.decode(test_ids)
            print(f"{text}")
            
            if is_valid_prefix(text, functions):
                selected_token = int(logit)
                break

        if selected_token is None:
            selected_token = int(np.argmax(logits))

        input_ids.append(selected_token)
        result.append(selected_token)

        if search_for_fn(llm.decode(result).split()[-1], functions):
            p_key_ids = list(llm.encode(' "parameters": {"')[0])
            input_ids += p_key_ids
            result.extend(p_key_ids)

        if is_json_complete(llm.decode(result)):
            break

    return llm.decode(result)

def search_for_fn(last_item, functions):
    """
        this function checks if function name is exitst in result plus ','
        for adding '"prompt": ' key to result without letting llm pridect it
    """
    tmp = last_item.replace('"', "")
    fn = tmp.replace(",", "")
    if "," in tmp and fn in functions:
        return True
    return False

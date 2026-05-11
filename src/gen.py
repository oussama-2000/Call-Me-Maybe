import json
import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()



FUNCTIONS = {
    "fn_add_numbers": ["a", "b"],
    "fn_greet": ["name"],
    "fn_reverse_string": ["s"],
    "fn_get_square_root": ["a"],
    "fn_substitute_string_with_regex": [
        "source_string",
        "regex",
        "replacement"
    ]
}

def build_prompt(user_prompt):

    return f"""
    You convert user requests into function calls.
    
    Return ONLY valid JSON. Do not explain. Do not repeat the prompt.
    
    Format:
    {{
    "prompt": string,
    "name": enum["fn_add_numbers", "fn_greet", "fn_reverse_string", "fn_get_square_root", "fn_substitute_string_with_regex"],
    "parameters": object
    }}
    
    Examples:
    
    User: What is the sum of 2 and 3?
    Output:
    {{"prompt": prompt, "name": "fn_add_numbers", "parameters": {{"a": 2, "b": 3}}}}
    
    User: Greet shrek
    Output:
    {{"prompt": prompt", "name": "fn_greet", "parameters": {{"name": "shrek"}}}}
    
    User: Reverse the string 'hello'
    Output:
    {{"prompt": prompt, "name": "fn_reverse_string", "parameters": {{"s": "hello"}}}}
    
    User: What is the square root of 16?
    Output:
    {{"prompt": prompt, "name": "fn_get_square_root", "parameters": {{"a": 16}}}}
    
    User: Replace all digits in 'abc123' with '#'
    Output:
    {{"prompt": prompt, "name": "fn_substitute_string_with_regex", "parameters": {{"source_string": "abc123", "regex": "\\\\d", "replacement": "#"}}}}
    
    Task:
    User: {user_prompt}
    Output:
    """


def is_valid_prefix(text: str) -> bool:
    """
    Checks whether the generated text can STILL become valid.

    This is PREFIX validation,
    not full JSON validation.
    """

    # Must start with {
    if not text.strip().startswith("{"):
        return False

    # Quick structural checks
    if text.count("{") < text.count("}"):
        return False

    if text.count('"') % 2 == 1:
        # inside unfinished string -> still valid
        pass

    # Reject invalid function names early
    if '"name"' in text:
        try:
            partial = text.split('"name"')[1]
    
            if ":" in partial:
                value_part = partial.split(":", 1)[1].strip()
    
                if value_part.startswith('"'):
    
                    current = value_part[1:]
    
                    is_closed = '"' in current
    
                    current = current.split('"')[0]
    
                    valid_prefix = any(
                        fn.startswith(current)
                        for fn in FUNCTIONS
                    )
    
                    valid_complete = current in FUNCTIONS
    
                    if is_closed:
                        if not valid_complete:
                            return False
                    else:
                        if not valid_prefix:
                            return False
    
        except Exception:
            return False

    return True


def is_json_complete(text: str) -> bool:
    try:
        obj = json.loads(text)
    
        # basic schema validation
        if not isinstance(obj, dict):
            return False
    
        required = ["prompt", "name", "parameters"]
    
        for k in required:
            if k not in obj:
                return False
    
        if obj["name"] not in FUNCTIONS:
            return False
    
        return True

    except Exception:
        return False



def generate(prompt, max_tokens=110, top_k=20):

    input_ids = llm.encode(prompt)[0].tolist()
    result = []

    for _ in range(max_tokens):

        logits = llm.get_logits_from_input_ids(input_ids)

        logits = np.array(logits)

        # get top-k candidates
        top_candidates = np.argsort(logits)[-top_k:]

        selected_token = None

        # try best candidates first
        for candidate in reversed(top_candidates):

            test_ids = input_ids + [int(candidate)]

            text = llm.decode(test_ids)

            if is_valid_prefix(text):

                selected_token = int(candidate)
                break

        # fallback
        if selected_token is None:
            selected_token = int(np.argmax(logits))

        input_ids.append(selected_token)
        result.append(selected_token)

        current_text = llm.decode(result)

        # print(current_text)

        if is_json_complete(current_text):
            break

    return llm.decode(result)


# generator = Generator()

# prompt = build_prompt("Replace all vowels in 'Programming is fun' with asterisks")

# output = generate(llm, prompt)

# print(output)
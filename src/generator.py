"""LLM + decoding"""

from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()


def build_prompt(user_prompt):
    return f"""
    You convert user requests into function calls.

    Return ONLY valid JSON. Do not explain. Do not repeat the prompt.

    Format:
    {{
      "prompt": string,
      "name": string,
      "parameters": object
    }}

    Examples:

    User: What is the sum of 2 and 3?
    Output:
    {{"prompt": "What is the sum of 2 and 3?", "name": "fn_add_numbers", "parameters": {{"a": 2, "b": 3}}}}

    User: Greet shrek
    Output:
    {{"prompt": "Greet shrek", "name": "fn_greet", "parameters": {{"name": "shrek"}}}}

    User: Reverse the string 'hello'
    Output:
    {{"prompt": "Reverse the string 'hello'", "name": "fn_reverse_string", "parameters": {{"s": "hello"}}}}

    User: What is the square root of 16?
    Output:
    {{"prompt": "What is the square root of 16?", "name": "fn_get_square_root", "parameters": {{"a": 16}}}}

    User: Replace all digits in 'abc123' with '#'
    Output:
    {{"prompt": "Replace all digits in 'abc123' with '#'", "name": "fn_substitute_string_with_regex", "parameters": {{"source_string": "abc123", "regex": "\\\\d", "replacement": "#"}}}}

    Task:
    User: {user_prompt}
    Output:
    """


def is_json_complete(text: str) -> bool:
    opened = text.count("{")
    closed = text.count("}")
    return opened > 0 and opened == closed


def extract_json(output):
    output = output[::-1]
    i = 0
    end = 0
    for c in output:
        if i == 4:
            break
        if c in "{}":
            i += 1

        end += 1
    json = output[:end]
    return json[::-1]


def generate(llm, prompt, max_tokens=100):
    input_ids = llm.encode(prompt)[0].tolist()

    for _ in range(max_tokens):
        logits = llm.get_logits_from_input_ids(input_ids)

        next_token = logits.index(max(logits))
        input_ids.append(next_token)
        text = llm.decode(input_ids)
        if is_json_complete(text):
            break
    result = llm.decode(input_ids)

    return result


prompt = build_prompt("what is the sum of 2 and 1?")
output = generate(llm, prompt)
print(extract_json(output))

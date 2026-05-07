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


def allowed_tokens(state):
    tokens = {
        "start": '{',
        "cot": '"',
        "name": "name",
        "dots": '":',
        "space": ' '
        
    }
    return tokens[state]

def update_state(state):
    next_state = {
        "start": "cot",
        "cot": "name",
        "name": "dots",
        "dots": "space"
    }
    return next_state[state]

def generate(llm, prompt, max_tokens=100):
    input_ids = llm.encode(prompt)[0].tolist()
    result = []
    state = "start"
    fn = llm.encode("fn")
    check = False
    fns = None
    
    for _ in range(max_tokens):
        logits = llm.get_logits_from_input_ids(input_ids)

        filtered = np.full_like(logits, float("-inf"))
        token = llm.encode(allowed_tokens(state))
        
        # filtered[token] = logits[token]
        # filtered[allowed_strings] = logits[allowed_strings]
        
        
        next_token = logits.index(max(logits))
        if next_token == fn:
            check = True
        # print(llm.decode(next_token))
        input_ids.append(next_token)
        result.append(next_token)
        print(llm.decode(result))
        text = llm.decode(input_ids)

        if is_json_complete(text):
            break

        if state != "space":
            state = update_state(state)
        
    return llm.decode(result)


prompt = build_prompt("what is the sum of 2 and 1?")
output = generate(llm, prompt)
print(output)

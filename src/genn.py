import json
import numpy as np
from llm_sdk.llm_sdk import Small_LLM_Model

llm = Small_LLM_Model()

# =========================================================
# FUNCTION SCHEMA
# =========================================================

FUNCTIONS = {
    "fn_add_numbers": {
        "a": "number",
        "b": "number"
    },

    "fn_greet": {
        "name": "string"
    },

    "fn_reverse_string": {
        "s": "string"
    },

    "fn_get_square_root": {
        "a": "number"
    },

    "fn_substitute_string_with_regex": {
        "source_string": "string",
        "regex": "string",
        "replacement": "string"
    },

    "fn_unknown": {}
}


# =========================================================
# STATE MACHINE
# =========================================================

class DecoderState:

    def __init__(self):

        self.stage = "FUNCTION_NAME"

        self.function_name = ""

        self.params = []

        self.param_index = 0

        self.current_value = ""

        self.finished = False


# =========================================================
# HELPERS
# =========================================================

def encode_text(llm, text):
    return llm.encode(text)[0].tolist()


def append_text(llm, text, input_ids, result):
    ids = encode_text(llm, text)

    input_ids.extend(ids)
    result.extend(ids)


def token_text(llm, token_id):
    return llm.decode([token_id])


# =========================================================
# FUNCTION NAME CONSTRAINTS
# =========================================================

def valid_function_prefix(prefix):

    for fn in FUNCTIONS.keys():

        if fn.startswith(prefix):
            return True

    return False


def function_finished(prefix):

    return prefix in FUNCTIONS


# =========================================================
# NUMBER VALIDATION
# =========================================================

def valid_number_prefix(text):

    allowed = set("0123456789.-")

    return all(c in allowed for c in text)


# =========================================================
# MAIN GENERATOR
# =========================================================

def generate(user_prompt, max_tokens=50):

    state = DecoderState()

    # ---------------------------------------------
    # deterministic prefix
    # ---------------------------------------------

    prefix = '{"name":"'

    input_ids = encode_text(llm, user_prompt)

    result = []

    append_text(llm, prefix, input_ids, result)

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for _ in range(max_tokens):

        logits = llm.get_logits_from_input_ids(input_ids)

        logits = np.array(logits)

        top_candidates = np.argsort(logits)[-20:]

        selected_token = None

        # =================================================
        # TRY CANDIDATES
        # =================================================

        for candidate in reversed(top_candidates):

            candidate = int(candidate)

            piece = token_text(llm, candidate)

            # =============================================
            # FUNCTION NAME STAGE
            # =============================================

            if state.stage == "FUNCTION_NAME":

                new_name = state.function_name + piece

                if valid_function_prefix(new_name):

                    selected_token = candidate

                    break

            # =============================================
            # PARAM VALUE STAGE
            # =============================================

            elif state.stage == "PARAM_VALUE":

                param_name = state.params[state.param_index]

                param_type = FUNCTIONS[state.function_name][param_name]

                # -----------------------------------------
                # NUMBER PARAM
                # -----------------------------------------

                if param_type == "number":

                    test = state.current_value + piece

                    if valid_number_prefix(test):

                        selected_token = candidate

                        break

                # -----------------------------------------
                # STRING PARAM
                # -----------------------------------------

                elif param_type == "string":

                    selected_token = candidate
                    break

        # =================================================
        # FALLBACK
        # =================================================

        if selected_token is None:

            selected_token = int(np.argmax(logits))

        # =================================================
        # APPLY TOKEN
        # =================================================

        piece = token_text(llm, selected_token)

        input_ids.append(selected_token)
        result.append(selected_token)

        # =================================================
        # UPDATE STATE
        # =================================================

        # -------------------------------------------------
        # FUNCTION NAME
        # -------------------------------------------------

        if state.stage == "FUNCTION_NAME":

            state.function_name += piece

            # function completed
            if function_finished(state.function_name):

                # deterministic structure
                append_text(
                    llm,
                    '","parameters":{',
                    input_ids,
                    result
                )

                state.params = list(
                    FUNCTIONS[state.function_name].keys()
                )

                # no params
                if len(state.params) == 0:

                    append_text(llm, "}}", input_ids, result)

                    state.finished = True

                    break

                # inject first param key
                first_param = state.params[0]

                append_text(
                    llm,
                    f'"{first_param}":',
                    input_ids,
                    result
                )

                state.stage = "PARAM_VALUE"

        # -------------------------------------------------
        # PARAM VALUE
        # -------------------------------------------------

        elif state.stage == "PARAM_VALUE":

            state.current_value += piece

            param_name = state.params[state.param_index]

            param_type = FUNCTIONS[state.function_name][param_name]

            # ---------------------------------------------
            # SIMPLE END DETECTION
            # ---------------------------------------------

            finished = False

            if param_type == "number":

                if piece in [",", "}"]:

                    finished = True

            elif param_type == "string":

                # crude heuristic
                if piece == '"':

                    finished = True

            # ---------------------------------------------
            # NEXT PARAM
            # ---------------------------------------------

            if finished:

                state.param_index += 1

                state.current_value = ""

                # all params done
                if state.param_index >= len(state.params):

                    append_text(llm, "}}", input_ids, result)

                    state.finished = True

                    break

                # next param
                next_param = state.params[state.param_index]

                append_text(
                    llm,
                    f',"{next_param}":',
                    input_ids,
                    result
                )
        print(llm.decode(result))
    return llm.decode(result)

def build_prompt(user_prompt, functions):
    return f"""
    You convert user requests into function calls.
    
    RETURN ONLY VALID MINIFIED JSON.
    
    Format:
    {{
      "name": string,
      "parameters": object
    }}

    FUNCTIONS:
    {functions}
    
    YOU MUST RESPECT PARAMETERS TYPE.
    
    Task:
    User prompt: {user_prompt}
    JSON:
    """

prompt = "Replace all numbers in \"Hello 34 I'm 233 years old\" with NUMBERS"
print(generate(build_prompt(prompt, FUNCTIONS)))
main parts:
    Input handling (parsing files)
    LLM generation (core logic)
    Output writing



input_ids = model.encode(prompt)

while not finished:
    logits = model.get_logits_from_input_ids(input_ids)

    valid_tokens = apply_constraints(logits, current_state)

    next_token = select(valid_tokens)

    input_ids.append(next_token)



https://www.youtube.com/watch?v=NKnZYvZA7w4
https://www.youtube.com/watch?v=AMdG7IjgSPM&t=1173s
https://www.youtube.com/shorts/KHEtJUlpqcg

https://jdmeier.com/how-llms-work/

cd ~/goinfre/Call-Me-Maybe
export XDG_CACHE_HOME=$PWD/.cache
export TMPDIR=$PWD/.tmp
uv add dependencies
<i>This project has been created as part of the 42 curriculum by oamkhou .</i>
<h1>Description</h1>
<ul>
    Call-Me-Maybe is a lightweight local LLM inference engine designed to convert natural language prompts into structured function calls using constrained decoding.

    The project uses Hugging Face models and implements a custom state-machine decoder to guarantee valid JSON generation while minimizing hallucinations and formatting errors.

    Instead of allowing the language model to freely generate output, deterministic JSON syntax is injected manually while the model is constrained to generate only semantic values such as:

    - function names
    - numbers
    - strings
    - regex expressions

    The goal of the project is to explore how modern LLM inference systems work internally and how constrained decoding can improve reliability, speed, and structured generation.
</ul>

<h1>Instructions</h1>

<ul>
    <h2>Installation</h2>
    <ul>
        <li>create virtual enviroment:</li>
        <code>uv venv or make venv</code>
        <li>activate it:</li>
        <code>source .venv/bin/activate</code>
        <li>install dependencies:</li>
        <code>uv sync</code>
    </ul>
    <h2>Usage</h2>
    <ul>
        <li>run program</li>
        <code>
            uv run python -m src
            --functions_definition examples/functions.json
            --input examples/prompts.json
            --output output/result.json
        </code>
        <li>example input</li>
        <code>
            [
                {
                    "prompt": "What is the sum of 2 and 3?"
                }
            ]
        </code>
        <li>example output</li>
        <code>
            [
                {
                    "prompt": "What is the sum of 2 and 3?",
                    "name": "fn_add_numbers",
                    "parameters": {
                        "a": 2.0,
                        "b": 3.0
                    }
                }
            ]
        </code>
    </ul>
</ul>

<h1>Resources</h1>
<ul>
    <h2>Classic References</h2>
    <ul>
        <li>Article</li>
        <a src="https://jdmeier.com/how-llms-work/">How LLMs Work</a>
        <li>Youtube</li>
        <ul>
            <a src="https://www.youtube.com/watch?v=AMdG7IjgSPM&t=1173s">
Python Tutorial: UV - A Faster, All-in-One Package Manager to Replace Pip and Venv</a>
        <br/>
            <a src="https://www.youtube.com/watch?v=NKnZYvZA7w4">How LLMs Actually Generate Text</a>
        <br/>
            <a src="https://www.youtube.com/shorts/KHEtJUlpqcg">LLMs are next-word predictors</a>
        <br/>
            <a src="https://youtu.be/ZXiruGOCn9s?si=9nLs4wAPtLDusXF1">
What are Transformers (Machine Learning Model)?</a>
            <br/>
            <a src="https://youtu.be/r1bquDz5GGA?si=rvwFW9dY5vU1AlE9">
            PyTorch in 1 Hour</a>
        </ul>
        <li>AI</li>
        <ul>
            generally i used AI to make the project subject more clear .
        </ul>
    </ul>
</ul>

<h1>Algorithm explanation</h1>
<ul>
    i used top k logits candidate methodology to treat just the top logits (the tokens that have bigeast score).
    then constrained decoding functions (is_valid_prefix(), is_json_complete())
    to constraine any llm generated token to avoid llm hallucination and wrong output.
    in everty generated token, i'm checking if the result (previous tokens and current token)
    still valid using is_valid_prefix(); such as json structur, function name, parameters validation .
    if the the current token verified as a valid i choose it and add it to the context, otherwise i will choose other candidate. 
    the function  is_json_complete() comes to verify if the generated json completed or not yet to break generation .
</ul>

<h1>Design decisions</h1>
<ul>
    i shoose that methodology because between many methods it comes with lateast time complexity, and maybe it more simple.
</ul>
<h1>Performance analysis</h1>
<ul>
    <h3>Accuracy</h3>
    <ul>
        the constrined decoder impove json validation, function name correctness and parameter consistency.
    </ul>
    <h3>Speed</h3>
    <ul>
        reduced token generation, top k constrained candidate selection and incremental validation.
    </ul>
    <h3>Reliability</h3>
    <ul>
        the decoder prevents invalid function names , malformed json invalid parameter keys and type mismatches.
    </ul>
</ul>
<h1>Challenges faced</h1>
<ul>
    <h3>Regex Escaping</h3>
    <ul>
        regex strings such as "\\d+\\" caused invalid json issues due to escaping conflicts between python strings, json encoding and regex syntax.
    </ul>
    <h3>GPU Memory & Disk Space</h3>
    <ul>
        Downloading transformer models on 42 machines caused cache overflow and cuda device mismatch.
    </ul>
</ul>
<h1>Testing strategy</h1>
<ul>
    The implementation was validated using:
    <ul>
        <li>valid function prompts</li>
        <li>invalid prompts</li>
        <li>unknown functions</li>
        <li>numeric edge cases</li>
        <li>regex-heavy inputs</li>
        <li>malformed generation attempts</li>
    </ul>
    Testing included:
    <ul>
        <li>JSON validation</li>
        <li>schema validation</li>
        <li>constrained decoding correctness</li>
        <li>output determinism</li>
    </ul>
</ul>

cd ~/goinfre/Call-Me-Maybe
export XDG_CACHE_HOME=$PWD/.cache
export TMPDIR=$PWD/.tmp

activate_uv:
	source $HOME/.local/bin/env
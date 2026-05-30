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
        <a href="https://jdmeier.com/how-llms-work/">How LLMs Work</a>
        <li>Youtube</li>
        <ul>
            <a href="https://www.youtube.com/watch?v=AMdG7IjgSPM&t=1173s">
Python Tutorial: UV - A Faster, All-in-One Package Manager to Replace Pip and Venv</a>
        <br/>
            <a href="https://www.youtube.com/watch?v=NKnZYvZA7w4">How LLMs Actually Generate Text</a>
        <br/>
            <a href="https://www.youtube.com/shorts/KHEtJUlpqcg">LLMs are next-word predictors</a>
        <br/>
            <a href="https://youtu.be/ZXiruGOCn9s?si=9nLs4wAPtLDusXF1">
What are Transformers (Machine Learning Model)?</a>
            <br/>
            <a href="https://youtu.be/r1bquDz5GGA?si=rvwFW9dY5vU1AlE9">
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
    To improve generation reliability, I implemented a Top-K candidate selection strategy combined with constrained decoding. Instead of considering the entire vocabulary at each generation 		step, the model only evaluates the top-K tokens with the highest logits (prediction scores). This significantly reduces the search space while preserving the most likely candidates.<br/>
	For each candidate token, I use validation functions such as is_valid_prefix() and is_json_complete() to ensure that the generated output remains syntactically and semantically correct. 		During generation, the candidate token is temporarily appended to the previously generated tokens, and the resulting text is validated. The is_valid_prefix() function checks that the partial 	output still conforms to the expected structure, including JSON syntax, valid function names, parameter names, and other schema constraints. If a candidate violates any constraint, it is 		rejected and the next best candidate is evaluated.<br/>
	Once a valid token is found, it is added to the context and generation continues. This process prevents hallucinated function names, malformed JSON, and invalid parameter structures. 			Finally, the is_json_complete() function determines whether a complete and valid JSON object has been generated, allowing the decoding loop to terminate as soon as the desired output is produced.<br/>
	This approach combines the flexibility of language models with deterministic validation rules, resulting in more accurate, reliable, and structured function-calling outputs.
</ul>

<h1>Design decisions</h1>
<ul>
    i shose that methodology between many methods because  it comes with lateast time complexity, and maybe it more simple.
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

"""LLM + decoding"""

from llm_sdk.llm_sdk import Small_LLM_Model
llm = Small_LLM_Model()
ids = llm.encode("hello")
print(ids)

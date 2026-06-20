from langchain_ollama import ChatOllama

# Centralized LLM instance used by every agent node.
# temperature=0 keeps structured-output generation deterministic and
# reduces the chance of the model inventing columns that don't exist.
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0,
)
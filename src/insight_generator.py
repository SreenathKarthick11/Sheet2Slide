from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)

def generate_insights(summary,analysis):

    prompt = f"""
        You are a business analyst.

        Dataset Summary:
        {summary}

        Statistics:
        {analysis}

        Generate:

        1. Key findings
        2. Trends
        3. Risks

        Keep it concise.
        """

    response = llm.invoke(prompt)

    return response.content
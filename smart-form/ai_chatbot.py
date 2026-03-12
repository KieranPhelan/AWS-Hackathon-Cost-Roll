"""File to send enquiry to the LLM and returns structured output."""


from dotenv import load_dotenv
from openai import OpenAI


SYSTEM_PROMPT = """

"""

DOC_PATH = "/path/to/knowledge_base.docx"


def analyse_enquiry(client: OpenAI,
                    message: str,
                    model: str = "gpt-5-nano"):
    """."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    )

    return response.choices[0].message.content


def analyse_enquiry(client: OpenAI,
                    message: str,
                    model: str = "gpt-5-nano",
                    use_rag: bool = True) -> AssistantAnalysis:
    """Analyse a customer enquiry and return structured output."""

    rag_context = ""
    if use_rag:
        rag_context = get_rag_context(message, DOC_PATH)
        prompt = f"{SYSTEM_PROMPT}\n\nRelevant Context:\n{rag_context}"
    else:
        prompt = SYSTEM_PROMPT

    response = client.responses.parse(
        model=model,
        instructions=prompt,
        input=[{"role": "user", "content": message}],
        text_format=AssistantAnalysis,
    )

    return response.output_parsed


if __name__ == "__main__":

    load_dotenv()

    client = OpenAI()

    response = analyse_enquiry(client, "How do I access my account?")

    print(response)

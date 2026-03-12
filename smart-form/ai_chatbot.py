"""File to send enquiry to the LLM and returns structured output."""


from dotenv import load_dotenv
from openai import OpenAI
from rag import get_rag_context


SYSTEM_PROMPT = """

"""

DOC_PATH = "docs/RAG-Doc-2.txt"


def analyse_enquiry(client: OpenAI,
                    message: str,
                    model: str = "gpt-4o-mini",
                    use_rag: bool = True):
    """Analyse a customer enquiry and return structured output."""

    rag_context = ""
    if use_rag:
        rag_context = get_rag_context(message, DOC_PATH)
        prompt = f"{SYSTEM_PROMPT}\n\nRelevant Context:\n{rag_context}"
    else:
        prompt = SYSTEM_PROMPT

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    load_dotenv()

    client = OpenAI()

    response = analyse_enquiry(
        client, "What is the difference between procurement type E and F?")

    print(response)

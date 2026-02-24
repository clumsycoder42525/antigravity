from app.llm import get_llm
from app.prompt import get_prompt
from langchain_core.output_parsers import StrOutputParser

def get_chain():
    llm = get_llm()
    prompt = get_prompt()
    parser = StrOutputParser()

    # NEW LangChain LCEL style
    chain = prompt | llm | parser
    return chain

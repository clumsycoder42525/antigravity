from langchain_core.prompts import ChatPromptTemplate

def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Answer clearly and concisely."),
        ("human", "{question}")
    ])

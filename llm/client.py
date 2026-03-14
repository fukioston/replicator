from langchain_openai import ChatOpenAI


def build_llm(config: dict) -> ChatOpenAI:
    return ChatOpenAI(
        model=config["llm_model"],
        base_url=config["llm_base_url"],
        api_key=config["llm_api_key"],
        temperature=0.3,
        max_tokens=4096,
    )

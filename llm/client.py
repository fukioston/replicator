from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


def build_llm(config: dict) -> BaseChatModel:
    provider = config.get("llm_provider", "openai_compatible")

    if provider == "anthropic":
        return ChatAnthropic(
            model=config["llm_model"],
            api_key=config["llm_api_key"],
            temperature=0.3,
            max_tokens=4096,
        )

    # OpenAI-compatible: DeepSeek, GLM, Kimi, MiniMax, etc.
    return ChatOpenAI(
        model=config["llm_model"],
        base_url=config["llm_base_url"],
        api_key=config["llm_api_key"],
        temperature=0.3,
        max_tokens=4096,
    )

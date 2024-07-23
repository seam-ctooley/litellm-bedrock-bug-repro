from typing import Annotated, Literal

from autogen import AssistantAgent, UserProxyAgent

chatbot = AssistantAgent(
    name="chatbot",
    system_message="For currency exchange tasks, only use the functions you have been provided with. Reply TERMINATE when the task is done.",
    llm_config={
        "config_list": [
            {
                "model": "claude3.5",  # Loaded with LiteLLM command
                "api_key": "NotRequired",  # Not needed
                "base_url": "http://localhost:4000/",  # Your LiteLLM URL
            }
        ],
        "cache_seed": None,
    },
)

# create a UserProxyAgent instance named "user_proxy"
user_proxy = UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "")
    and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

CurrencySymbol = Literal["USD", "EUR"]


def exchange_rate(
    base_currency: CurrencySymbol, quote_currency: CurrencySymbol
) -> float:
    if base_currency == quote_currency:
        return 1.0
    elif base_currency == "USD" and quote_currency == "EUR":
        return 1 / 1.1
    elif base_currency == "EUR" and quote_currency == "USD":
        return 1.1
    else:
        raise ValueError(f"Unknown currencies {base_currency}, {quote_currency}")


@user_proxy.register_for_execution()
@chatbot.register_for_llm(description="Currency exchange calculator.")
def currency_calculator(
    base_amount: Annotated[float, "Amount of currency in base_currency"],
    base_currency: Annotated[CurrencySymbol, "Base currency"] = "USD",
    quote_currency: Annotated[CurrencySymbol, "Quote currency"] = "EUR",
) -> str:
    quote_amount = exchange_rate(base_currency, quote_currency) * base_amount
    return f"{quote_amount} {quote_currency}"


res = user_proxy.initiate_chat(chatbot, message="How much is 123.45 USD in EUR?")

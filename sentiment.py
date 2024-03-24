from __future__ import annotations

from typing import TypedDict, Literal, NotRequired
import requests

from config import load_config, ConfigType

# Configuration from the config file
config: ConfigType = load_config("./config.json")


class SentimentResponse(TypedDict):
    """
    Class used for type hints of sentiment queries.
    """
    score: int
    label: Literal['negative', 'neutral', 'positive']


class SentimentRequestOptions(TypedDict):
    """
    Class used for type hints of sentiment query options.
    """
    use_cache: NotRequired[bool]
    wait_for_model: NotRequired[bool]


class SentimentRequest(TypedDict):
    """
    Class used for type hints of sentiment queries.
    """
    inputs: str | list[str]
    # By default, both flags set to True
    options: NotRequired[SentimentRequestOptions]


def query(payload: SentimentRequest) -> list[list[SentimentResponse]]:
    """
    Queries an NLP sentiment model using its serverless API.
    :param payload: request to the sentiment model.
    :return:
    """

    # Add the options to payload of not present
    if 'options' not in payload:
        payload['options'] = {
            'use_cache': True,      # Use caching
            'wait_for_model': True  # Wait for the model if not booted (cold starts)
        }

    # For documentation of requests consult: https://docs.python-requests.org/en/latest/user/advanced/
    # For documentation of API check config.json for API link
    response = requests.post(
        config['hf']['sentiment_url'],
        headers={
            "Authorization": config['hf']['sentiment_token']
        },
        json=payload,
        proxies=config['proxies']
    )

    return response.json()

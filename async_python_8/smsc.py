import logging
from typing import Dict, Any
from urllib import parse

import asks
from asks import response_objects as asks_response, errors

SMSC_BASE_URL: str = "https://smsc.ru/sys/"
SMSC_FMT_JSON: int = 3
SMSC_METHOD_SEND: str = "send"
SMSC_METHOD_STATUS: str = "status"


class SMSCApiError(Exception):
    """raised in case of sms gateway api errors"""


async def request_smsc(
        session: asks.Session,
        method: str,
        login: str,
        password: str,
        payload: Dict[str, str],
) -> Dict[str, Any]:
    """Send request to SMSC.ru service"""

    endpoint: str = f"{method}.php"
    endpoint_url: str = parse.urljoin(SMSC_BASE_URL, endpoint)

    params = {
        "login": login,
        "psw": password,
        "fmt": SMSC_FMT_JSON,
        "charset": "utf-8",
    }
    params.update(payload)
    try:
        response: asks_response.Response = await session.post(
            url=endpoint_url,
            params=params,
        )
        response.raise_for_status()
    except errors.AsksException as e:
        logging.error(str(e))
        raise SMSCApiError("request to smsc.ru failed")

    try:
        response_body = response.json()
        if "error" in response_body:
            raise SMSCApiError(response_body)
    except (ValueError, TypeError) as e:
        logging.error("\n".join(str(e)))
        raise SMSCApiError("unable to parse json response from smsc.ru")
    else:
        return response_body

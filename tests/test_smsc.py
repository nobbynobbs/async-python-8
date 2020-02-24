from unittest import mock
import json

import pytest

from asks import errors

import async_python_8.smsc


@pytest.fixture
def session():
    return mock.MagicMock()


async def test_send_request(session):
    """success case"""
    async def post(*args, **kwargs):
        response = mock.MagicMock()
        response.json = mock.MagicMock(return_value={"id": 53, "cnt": 1})
        return response

    session.post = post
    result = await async_python_8.smsc.request_smsc(session, "send", "test", "test", {
        "phones": "+79305551234",
        "mes": "Привет, Мир!",
    })
    assert result == {"id": 53, "cnt": 1}


async def test_send_request_error(session):
    """
    check if exception raised
    in case of attribute "error" exists in response body
    """
    async def post(*args, **kwargs):
        response = mock.MagicMock()
        response.json = mock.MagicMock(
            return_value={
                "error_code": 1,
                "error": "wrong parameters"
            })
        return response

    with pytest.raises(async_python_8.smsc.SMSCApiError):
        session.post = post
        await async_python_8.smsc.request_smsc(session, "send", "test", "test", {})


async def test_send_request_exception(session):
    """check if asks exception caught and SMSCApiError reraised"""

    async def post(*args, **kwargs):
        raise errors.AsksException("test exception")

    with pytest.raises(async_python_8.smsc.SMSCApiError):
        session.post = post
        await async_python_8.smsc.request_smsc(session, "send", "test", "test", {})


async def test_send_request_invalid_json():
    """
    check if exception raised
    in case of attribute "error" exists in response body
    """
    async def post(*args, **kwargs):
        response = mock.MagicMock()
        response.json = mock.MagicMock(
            side_effect=json.JSONDecodeError("", "", 0)
        )
        return response

    with pytest.raises(async_python_8.smsc.SMSCApiError):
        session.post = post
        await async_python_8.smsc.request_smsc(session, "send", "test", "test", {})

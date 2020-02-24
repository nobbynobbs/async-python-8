from async_python_8 import utils

import pytest


@pytest.mark.parametrize("info,result", [
    ({
        "sms_id": 1,
        "text": "qwerqwer",
        "created_at": 1582533910.1654646,
        "phones_count": 3,
        "phones": {
            "+79305551234": "delivered",
            "911": "failed",
            "112": "pending",
        }
    }, {
        "mailingId": "1",
        "SMSText": "qwerqwer",
        "timestamp": 1582533910.1654646,
        "totalSMSAmount": 3,
        "deliveredSMSAmount": 1,
        "failedSMSAmount": 1,
    }), ({
        "sms_id": 1,
        "text": "привет, мир",
        "created_at": 1582533910.1654646,
        "phones_count": 3,
        "phones": {
            "+79305551234": "pending",
            "911": "pending",
            "112": "pending",
        }
    }, {
        "mailingId": "1",
        "SMSText": "привет, мир",
        "timestamp": 1582533910.1654646,
        "totalSMSAmount": 3,
        "deliveredSMSAmount": 0,
        "failedSMSAmount": 0,
    }),
])
def test_convert_mailing_info(info, result):
    assert utils.convert_mailing_info(info) == result

from collections import Counter
from typing import Dict, Any


def convert_mailing_info(db_info: Dict[str, Any]) -> Dict[str, Any]:
    """convert information about mailing from storage format to format
    supported by frontend
    """
    print(db_info)
    counter = Counter(db_info["phones"].values())
    return {
        "timestamp": db_info["created_at"],
        "SMSText": db_info["text"],
        "mailingId": str(db_info["sms_id"]),
        "totalSMSAmount": db_info["phones_count"],
        "deliveredSMSAmount": counter["delivered"],
        "failedSMSAmount": counter["failed"],
    }

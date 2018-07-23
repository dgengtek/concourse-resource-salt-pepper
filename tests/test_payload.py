import pytest
import concsp.payload 


def test_load_payload(payload_check):
    payload = concsp.payload.ConcoursePayload()
    payload.init(payload_check)
    assert payload.source.get("uri") == "https://salt:8000"


def test_load_payload_missing_required(payload_check):
    del payload_check["source"]["uri"]
    payload = concsp.payload.ConcoursePayload()
    with pytest.raises(concsp.payload.ConcoursePayloadException):
        payload.init(payload_check)


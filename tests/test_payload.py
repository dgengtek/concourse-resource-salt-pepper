import pytest
from concsp.payload import ConcoursePayload,\
    ConcoursePayloadOut,\
    ConcoursePayloadException,\
    ConcoursePayloadSourceException,\
    ConcoursePayloadParameterException


def test_load_payload(payload_check):
    payload = ConcoursePayload()
    payload.init(payload_check)
    assert payload.source.get("uri") == "https://salt:8000"


def test_load_payload_missing_required(payload_check):
    del payload_check["source"]["uri"]
    payload = ConcoursePayload()
    with pytest.raises(ConcoursePayloadSourceException):
        payload.init(payload_check)


def test_empty_payload():
    payload = ConcoursePayload()
    with pytest.raises(ConcoursePayloadException):
        payload.init(None)


def test_init_twice(payload_check):
    payload = ConcoursePayload()
    payload.init(payload_check)
    with pytest.raises(ConcoursePayloadException):
        payload.init(payload_check)


def test_init_twice_with_reset(payload_check):
    payload = ConcoursePayload()
    payload.init(payload_check)
    assert payload.source.get("uri") == "https://salt:8000"
    del payload.source["uri"]
    assert "uri" not in payload.source
    payload.reset()
    payload.init(payload_check)
    assert payload.source.get("uri") == "https://salt:8000"


def test_retrieve_attribute_without_init():
    payload = ConcoursePayload()
    with pytest.raises(ConcoursePayloadException):
        payload.source.get("uri")


def test_retrieve_attribute_with_reset(payload_check):
    payload = ConcoursePayload()
    payload.init(payload_check)
    payload.reset()
    with pytest.raises(ConcoursePayloadException):
        payload.source.get("uri")


def test_payload_out(payload_out):
    payload = ConcoursePayloadOut()
    payload.init(payload_out)
    assert payload.tgt == "*"
    assert payload.fun == "test.ping"


def test_payload_out_mandatory(payload_out):
    del payload_out["params"]["tgt"]
    payload = ConcoursePayloadOut()
    with pytest.raises(ConcoursePayloadParameterException):
        payload.init(payload_out)


@pytest.mark.parametrize("key,value", [
    ("args", {}),
    ("args", ""),
    ("kwargs", []),
    ("kwargs", ""),
])
def test_payload_out_kwarg(payload_out, key, value):
    payload_out["params"][key] = value
    payload = ConcoursePayloadOut()
    with pytest.raises(ConcoursePayloadParameterException):
        payload.init(payload_out)

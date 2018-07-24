import pytest
import pepper
from concsp import salt
from concsp.payload import ResourcePayload
import error_mock
import json


@pytest.fixture()
def something():
    pass


@pytest.fixture
def payload_check():
    with open("tests/responses/check.json") as f:
        return json.load(f)


@pytest.fixture
def payload_out():
    with open("tests/responses/out.json") as f:
        return json.load(f)

@pytest.fixture()
def concourse_payload_check(payload_check):
    payload = ResourcePayload()
    payload.init(payload_check)
    return payload


@pytest.fixture()
def concourse_payload_out(payload_out):
    payload = ResourcePayload()
    payload.init(payload_out)
    return payload


@pytest.fixture(scope="module")
def salturl():
    return "https://salt:8000"


@pytest.fixture()
def api(concourse_payload_check):
    salt_pepper = pepper.Pepper(
            concourse_payload_check.uri,
            concourse_payload_check.debug_http,
            concourse_payload_check.verify_ssl)
    return salt.SaltAPI(salt_pepper, concourse_payload_check)


@pytest.fixture()
def api_authenticated(api, api_response):
    api.auth = api_response
    return api


@pytest.fixture()
def mock_req_200(mocker):
    mocker.patch.object(pepper.Pepper, "req", autospec=True)
    pepper.Pepper.req.return_value = {}


@pytest.fixture()
def api_response():
    return {'perms': [{'*': ['test.echo', 'cmd.run']}],
            'start': 1532188413.50455,
            'token': '1f1e160f5b64f4b67161a0563af21192203e34b2',
            'expire': 1532231613.504551,
            'user': 'concourse',
            'eauth': 'ldap'}


@pytest.fixture()
def api_401(monkeypatch, api):
    error_401 = error_mock.build_raise_http_error(None, 401)
    monkeypatch.setattr(pepper.libpepper, "urlopen",  error_401)
    return api


@pytest.fixture()
def api_500(monkeypatch, api):
    error_500 = error_mock.build_raise_http_error(None, 500)
    monkeypatch.setattr(pepper.libpepper, "urlopen",  error_500)
    return api

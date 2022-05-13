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
        concourse_payload_check.verify_ssl,
    )
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
    return {
        "perms": [{"*": ["test.echo", "cmd.run"]}],
        "start": 1532188413.50455,
        "token": "1f1e160f5b64f4b67161a0563af21192203e34b2",
        "expire": 1532231613.504551,
        "user": "concourse",
        "eauth": "ldap",
    }


@pytest.fixture()
def api_401(monkeypatch, api):
    error_401 = error_mock.build_raise_http_error(None, 401)
    monkeypatch.setattr(pepper.libpepper, "urlopen", error_401)
    return api


@pytest.fixture()
def api_500(monkeypatch, api):
    error_500 = error_mock.build_raise_http_error(None, 500)
    monkeypatch.setattr(pepper.libpepper, "urlopen", error_500)
    return api


@pytest.fixture()
def state_output():
    return [
        {
            "minion1": {
                "cmd_|-Run test command get ips_|-ifconfig_|-run": {
                    "comment": 'Command "ifconfig" would have been executed',
                    "name": "ifconfig",
                    "start_time": "20:59:43.546975",
                    "result": None,
                    "duration": 4.595,
                    "__run_num__": 3,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get ips",
                },
                "cmd_|-Run test command list dirs_|-ls /_|-run": {
                    "comment": 'Command "ls /" would have been executed',
                    "name": "ls /",
                    "start_time": "20:59:43.545041",
                    "result": None,
                    "duration": 0.639,
                    "__run_num__": 0,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command list dirs",
                },
                "cmd_|-Run test command get blks_|-lsblk_|-run": {
                    "comment": 'Command "lsblk" would have been executed',
                    "name": "lsblk",
                    "start_time": "20:59:43.546400",
                    "result": None,
                    "duration": 0.47,
                    "__run_num__": 2,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get blks",
                },
                "cmd_|-Run test command get uptime_|-uptime_|-run": {
                    "comment": 'Command "uptime" would have been executed',
                    "name": "uptime",
                    "start_time": "20:59:43.545837",
                    "result": None,
                    "duration": 0.457,
                    "__run_num__": 1,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get uptime",
                },
            }
        },
        {
            "minion2": {
                "cmd_|-Run test command get ips_|-ifconfig_|-run": {
                    "comment": 'Command "ifconfig" would have been executed',
                    "name": "ifconfig",
                    "start_time": "18:59:44.276802",
                    "result": None,
                    "duration": 0.564,
                    "__run_num__": 3,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get ips",
                },
                "cmd_|-Run test command list dirs_|-ls /_|-run": {
                    "comment": 'Command "ls /" would have been executed',
                    "name": "ls /",
                    "start_time": "18:59:44.274431",
                    "result": None,
                    "duration": 0.748,
                    "__run_num__": 0,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command list dirs",
                },
                "cmd_|-Run test command get blks_|-lsblk_|-run": {
                    "comment": 'Command "lsblk" would have been executed',
                    "name": "lsblk",
                    "start_time": "18:59:44.276096",
                    "result": None,
                    "duration": 0.569,
                    "__run_num__": 2,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get blks",
                },
                "cmd_|-Run test command get uptime_|-uptime_|-run": {
                    "comment": 'Command "uptime" would have been executed',
                    "name": "uptime",
                    "start_time": "18:59:44.275368",
                    "result": None,
                    "duration": 0.586,
                    "__run_num__": 1,
                    "__sls__": "test.state",
                    "changes": {},
                    "__id__": "Run test command get uptime",
                },
            }
        },
        {"minion3": "Minion did not return. [Not connected]"},
    ]

import pepper
import pytest


def test_login_server_error(api_500):
    with pytest.raises(pepper.PepperException):
        api_500.login()


def test_login_unauthorized(api_401):
    with pytest.raises(pepper.PepperException):
        api_401.login()


def test_logout_ok(api_authenticated, mock_req_200):
    if not api_authenticated.pepper.auth:
        api_authenticated.pepper.auth = {}
        api_authenticated.pepper.auth["token"] = "atoken"

    assert api_authenticated.logout() == {}


def test_logout_fail(api):
    with pytest.raises(pepper.PepperException):
        api.logout()

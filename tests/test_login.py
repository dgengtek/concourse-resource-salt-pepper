import pepper
import pytest


def test_login_server_error(api_500):
    with pytest.raises(pepper.PepperException):
        api_500.login(None, None)


def test_login_unauthorized(api_401):
    with pytest.raises(pepper.PepperException):
        api_401.login(None, None)


def test_logout_ok(api_authenticated, mock_req_200):
    assert api_authenticated.logout() == {}


def test_logout_fail(api):
    with pytest.raises(pepper.PepperException):
        api.logout()

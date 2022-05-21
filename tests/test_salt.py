from concsp.data import ReturnData


def test_poll_client_runner(
    mocker,
    api_patched,
    api_payload_runner_async,
    return_pepper_low_runner,
    return_runner_async,
):
    mocker.patch.object(
        api_patched.pepper,
        "low",
        side_effect=[return_pepper_low_runner, return_runner_async],
    )
    return_data = ReturnData.build_from_runner(return_runner_async)
    assert (0, return_data, []) == api_patched.poll_for_returns(
        api_payload_runner_async
    )


def test_poll_client_local(
    mocker, api_patched, api_payload, return_pepper_low, return_local_async
):
    mocker.patch.object(
        api_patched.pepper, "low", side_effect=[return_pepper_low, return_local_async]
    )
    return_data = ReturnData.build_from_local(return_local_async)
    assert (0, return_data, ["minion1"]) == api_patched.poll_for_returns(api_payload)

from concsp import data


def test_return_local_async(return_local_async):
    output = str(data.ReturnData.build_from_local(return_local_async))
    assert "==> minion1" in output
    assert "+service_|-start salt-api service_|-salt-api_|-running:" in output


def test_return_runner_async(return_runner_async):
    output = str(data.ReturnData.build_from_runner(return_runner_async))
    assert "==> minion1_master" in output
    assert "+salt_|-master_sync_modules_|-saltutil.sync_modules_|-runner:" in output

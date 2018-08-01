from concsp import salt
import pytest


@pytest.mark.skip()
def test_simple_output(state_output):
    for r in state_output:
        salt.print_result(0, r)
    assert False

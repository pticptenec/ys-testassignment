import pytest


@pytest.mark.run_only_from_cmd()
def test_main(insert_testdata):
    """Just populate db with testdata for manual testing"""
    assert 1 == 1

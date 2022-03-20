import pytest

from tests.e2e import load_testdata


@pytest.fixture(scope='function')
def testdata():
    yield load_testdata()

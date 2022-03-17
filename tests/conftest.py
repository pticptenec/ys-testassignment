import os
import json
from pathlib import Path

from songs.models import Song

import pytest


testdatadir = os.path.join(os.path.dirname(__file__), 'testdata')


@pytest.fixture(scope='session')
def testdata():
    yield load_testdata()


def load_testdata():
    data = []
    with open(Path(testdatadir) / 'songs.json', 'rt') as f:
        for line in f:
            data.append(Song(**json.loads(line)))

    return data

import json


def test_init(app):
    pass


def test_all_songs(client, testdata):
    response = client.get('/api/songs')
    expect = [
        json.loads(song.json())
        for song in sorted(
            testdata, key=lambda song: song.title
        )
    ]
    assert response.json() == expect

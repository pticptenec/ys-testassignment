import math


def dt_to_json(dt):
    return dt.strftime('%Y-%m-%d')


def test_all_songs_first_page(client, testdata):
    per_page = 3
    response = client.get('/api/songs')
    expect = [
        song.dict()
        for song in sorted(
            testdata, key=lambda song: song.title
        )
    ][:per_page]

    result = []
    for res, exp in zip(response.json['songs'], expect):
        exp['released'] = dt_to_json(exp['released'])
        del res['id']
        del exp['id']
        result.append(res)

    assert result == expect


def test_all_songs_last_page(client, testdata):
    per_page = 3
    last_page = math.ceil(len(testdata) / per_page)
    last_index = len(testdata) % per_page
    response = client.get(f'/api/songs?page={last_page}')
    expect = [
        song.dict()
        for song in sorted(
            testdata, key=lambda song: song.title
        )
    ][-last_index:]

    result = []
    for res, exp in zip(response.json['songs'], expect):
        exp['released'] = dt_to_json(exp['released'])
        del res['id']
        del exp['id']
        result.append(res)

    assert result == expect


def test_all_songs_middle_page(client, testdata):
    per_page = 3
    last_page = math.ceil(len(testdata) / per_page)
    mid_page = (1 + last_page) // 2
    response = client.get(f'/api/songs?page={mid_page}')
    expect = [
        song.dict()
        for song in sorted(
            testdata, key=lambda song: song.title
        )
    ][per_page:per_page * mid_page]

    result = []
    for res, exp in zip(response.json['songs'], expect):
        exp['released'] = dt_to_json(exp['released'])
        del res['id']
        del exp['id']
        result.append(res)

    assert result == expect


def test_songs_avg_difficulty_all(client, testdata):
    response = client.get('/api/songs/avg-difficulty')
    sum_ = sum(map(lambda song: song.difficulty, testdata))
    avg = sum_ / len(testdata)
    assert response.json == {
        'avg': round(avg, 2)
    }

def test_songs_avg_difficulty_filter_by_level(client, testdata):
    level = 5
    response = client.get(f'/api/songs/avg-difficulty?level={level}')
    filtered = list(filter(lambda song: song.level > level,
                    testdata))
    sum_ = sum(map(lambda song: song.difficulty,
               filtered))
    avg = sum_ / len(filtered)
    assert response.json == {
        'avg': round(avg, 2)
    }


def test_search(client, testdata):
    msg = 'awaki'
    response = client.get(f'/api/songs/search?message={msg}')
    filtered = filter(lambda song: msg in song.title.lower(),
                         testdata)
    expected = []
    results = []
    for item, result in zip(filtered, response.json['result']):
        exp = item.dict()
        del exp['id']
        del result['id']
        exp['released'] = dt_to_json(exp['released'])
        results.append(result)
        expected.append(exp)

    assert results == expected


def test_no_search_results(client):
    msg = 'tutu'
    response = client.get(f'/api/songs/search?message={msg}')
    assert response.json == {
        'result': [],
    }

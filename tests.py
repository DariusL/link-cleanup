import pytest

from link_cleanup import Pattern, Cleaner, clean_up_link, InputError


def test_unmatched_url_is_not_affected():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://abc.com') == 'https://abc.com'


def test_empty_cleaner_does_nothing():
    assert Cleaner().clean('https://abc.com') == 'https://abc.com'


def test_pattern_with_no_instructions_does_nothing():
    pattern = Pattern(['abc.com'])
    assert Cleaner(pattern).clean('https://abc.com') == 'https://abc.com'


def test_replace_url():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://foo.com') == 'https://bar.com'


def test_replace_url_with_path():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://foo.com/my/path') == 'https://bar.com/my/path'


def test_remove_single_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['si'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa') == 'https://foo.com/my/path'


def test_remove_first_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['si'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa&foo=bar') == 'https://foo.com/my/path?foo=bar'


def test_remove_last_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['foo'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa&foo=bar') == 'https://foo.com/my/path?si=aaa'


def test_remove_middle_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['bbb'])
    assert Cleaner(pattern).clean(
        'https://foo.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/my/path?aaa=aaa&ccc=ccc'


def test_remove_two_queries():
    pattern = Pattern(['foo.com'], queries_to_remove=['aaa', 'ccc'])
    assert Cleaner(pattern).clean(
        'https://foo.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/my/path?bbb=bbb'


def test_match_first_pattern():
    cleaner = Cleaner(
        Pattern(['bar.com'], queries_to_remove=['bbb']),
        Pattern(['foo.com'], queries_to_remove=['aaa']),
    )
    assert cleaner.clean('https://bar.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://bar.com/my/path?aaa=aaa&ccc=ccc'


def test_match_last_pattern():
    cleaner = Cleaner(
        Pattern(['foo.com'], queries_to_remove=['aaa']),
        Pattern(['bar.com'], queries_to_remove=['bbb']),
    )
    assert cleaner.clean('https://bar.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://bar.com/my/path?aaa=aaa&ccc=ccc'


def test_match_path():
    cleaner = Cleaner(
        Pattern(['foo.com'], target_paths=['/my/path'], queries_to_remove=['aaa']),
        Pattern(['foo.com'], queries_to_remove=['bbb']),
    )
    assert cleaner.clean('https://foo.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/my/path?bbb=bbb&ccc=ccc'


def test_ignore_pattern_unmatched_path():
    cleaner = Cleaner(
        Pattern(['foo.com'], target_paths=['/my/path'], queries_to_remove=['aaa']),
        Pattern(['foo.com'], queries_to_remove=['bbb']),
    )
    assert cleaner.clean(
        'https://foo.com/other/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/other/path?aaa=aaa&ccc=ccc'


test_cases = [
    ('spotify_track_1', 'https://open.spotify.com/track/7rK68oMQ3KYzsFRPaIdb3i?si=rYfLzNHzQCmgggzfBg',
     'https://open.spotify.com/track/7rK68oMQ3KYzsFRPaIdb3i'),
    ('spotify_track_2',
     'https://open.spotify.com/track/4pYuPkr13zQbrrDChQrfQs?si=dotOgggaTE-OhDyeeiyAOA&context=spotify%3Aplaylist%3A37i9dQZF1gggevO1aAyaE',
     'https://open.spotify.com/track/4pYuPkr13zQbrrDChQrfQs'),
    ('spotify_playlist',
     'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1aAyaE?si=8oBzjYVSRBORA6gggLeDw&pi=VwcIYn_gggKUv',
     'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1aAyaE'),
    ('spotify_artist', 'https://open.spotify.com/artist/244uLu9lkdw39BJwlul3k8?si=pf4uwzUzggg2Kv-oOFLe5hA',
     'https://open.spotify.com/artist/244uLu9lkdw39BJwlul3k8'),
    ('spotify_album',
     'https://open.spotify.com/album/2z6a4yNBjfxi9QvMheDR?si=dy-aG0I0S8C5SglopBvg&utm_source=copy-link',
     'https://open.spotify.com/album/2z6a4yNBjfxi9QvMheDR'),
    ('youtube_video_1', 'https://youtu.be/LMhResdylaE?t=64&is=o1MwcvgggSz8fsFY',
     'https://youtu.be/LMhResdylaE?t=64'),
    ('youtube_video_2', 'https://www.youtube.com/watch?v=LMhResdylaE&list=WL&index=1&t=5361s',
     'https://www.youtube.com/watch?v=LMhResdylaE&t=5361s'),
    ('youtube_playlist_1', 'https://youtube.com/playlist?list=PL9e7gmwejeGr7aqh9A4h4A0xgkveb8ld&si=TcNfjSHyIX__E4d',
     'https://youtube.com/playlist?list=PL9e7gmwejeGr7aqh9A4h4A0xgkveb8ld'),
    ('x_post', 'https://x.com/kmcnam1/status/2040858635086209325?s=20',
     'https://fixupx.com/kmcnam1/status/2040858635086209325'),
]


@pytest.mark.parametrize(
    ['tc_name', 'original', 'clean'], test_cases,
    ids=[name for (name, _, _) in test_cases]
)
def test_real_usage(tc_name, original, clean):
    assert clean_up_link(original) == {'status': 'success', 'url': clean}


@pytest.mark.parametrize(
    ['original'], [('',), (' ',), (None,)]
)
def test_empty_input(original):
    with pytest.raises(InputError, match='Missing input url'):
        Cleaner().clean(' ')

def test_invalid_input():
    with pytest.raises(InputError, match='Invalid input url "foo"'):
        Cleaner().clean('foo')


def test_clean_failure():
    assert clean_up_link(' ') == {'status': 'failure', 'message': 'Missing input url'}
